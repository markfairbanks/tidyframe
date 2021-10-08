import polars as pl
from polars import col, Series, when
import functools as ft

from typing import Union, List

def as_tibble(df):
    df.__class__ = tibble
    return df

def col_expr(x):
    if isinstance(x, pl.Expr):
        return x
    elif isinstance(x, str):
        return col(x)
    else:
       raise ValueError("Invalid input for column selection") 

#  Wrap all str inputs in col()  
def col_exprs(x):
    if is_list_like(x):
        return [col_expr(val) for val in x]
    else:
        return [col_expr(x)]
  
def is_list_like(x):
    if isinstance(x, list) | isinstance(x, pl.Series):
        return True
    else:
        return False

def as_list(x):
    if isinstance(x, list):
        return x.copy()
    elif isinstance(x, str):
        return [x]
    else:
        return list(x)

def args_as_list(x):
    if len(x) == 0:
        return []
    elif isinstance(x[0], list):
        return x[0]
    elif is_list_like(x[0]):
        return list(x[0])
    else:
        return [*x]

# Convert kwargs to col() expressions with alias
def kwargs_as_exprs(kwargs):
    return [expr.alias(key) for key, expr in kwargs.items()]

class tibble(pl.DataFrame):
    def arrange(self, *args, desc: Union[bool, List[bool]] = False) -> "tp.tibble":
        """
        Arrange/sort rows

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to sort by

        desc : Union[bool, List[bool]] = False
            Should columns be ordered in descending order

        Examples
        --------
        df = tp.tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        
        # Arrange in ascending order
        df.arrange('x', 'y')
        
        # Arrange some columns descending
        df.arrange('x', 'y', desc = [True, False])
        """
        exprs = args_as_list(args)
        return self.sort(exprs, reverse = desc).pipe(as_tibble)

    def bind_cols(self, df: "tp.tibble") -> "tp.tibble" :
        """
        Bind data frames by columns

        Parameters
        ----------
        df : tibble
            Data frame to bind

        Examples
        --------
        df1 = tp.tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        df2 = tp.tibble({'a': ['c', 'c', 'c'], 'b': range(4, 7)})

        df1.bind_cols(df2)
        """
        # TODO: Allow to work on multiple inputs
        return self.hstack(df).pipe(as_tibble)
    
    def bind_rows(self, df: "tp.tibble") -> "tp.tibble":
        """
        Bind data frames by row

        Parameters
        ----------
        df : tibble
            Data frame to bind

        Examples
        --------
        df1 = tp.tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        df2 = tp.tibble({'x': ['c', 'c', 'c'], 'y': range(4, 7)})

        df1.bind_rows(df2)
        """
        # TODO: Allow to work on multiple inputs
        return self.vstack(df).pipe(as_tibble)

    def distinct(self, *args) -> "tp.tibble":
        """
        Select distinct/unique rows

        Parameters
        ----------
        *args : Union[str, Expr]
            Column expressions find distinct/unique rows

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        
        df.distinct()

        df.distinct('b')
        """
        # TODO: Create for series
        args = args_as_list(args)

        if len(args) == 0:
            df = self.drop_duplicates()
        else:
            df = self.select(args).drop_duplicates()
        
        return df.pipe(as_tibble)

    def filter(self, *args) -> "tp.tibble":
        """
        Filter rows on one or more conditions

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        
        df.filter(col('a') < 2, col('c') == 'a')

        df.filter((col('a') < 2) & (col('c') == 'a'))
        """
        args = args_as_list(args)
        exprs = ft.reduce(lambda a, b: a & b, args)
        return super().filter(exprs).pipe(as_tibble)
    
    def group_by(self, *args):
        """
        Group by one or more variables

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        
        df.group_by('c')

        df.group_by('a', 'c')
        """
        args = args_as_list(args)
        df = self.groupby(args)
        df.__class__ = grouped_tibble
        return df
    
    def mutate(self, *args, **kwargs) -> "tp.tibble":
        """
        Add or modify columns

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3)})

        df.mutate(double_a = col('a') * 2,
                  a_plus_b = col('a') + col('b'))
        
        df.mutate((col(['a', 'b]) * 2).prefix('double_'),
                  a_plus_b = col('a') + col('b'))
        """
        exprs = args_as_list(args) + kwargs_as_exprs(kwargs)
        return self.with_columns(exprs).pipe(as_tibble)

    def pull(self, var = None):
        """
        Extract a column as a series

        Parameters
        ----------
        var : str
            Name of the column to extract. Defaults to the last column.

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3))
        
        df.pull('a')
        """
        if var == None:
            var = self.columns[-1]
        
        return self.get_column(var)
    
    def relocate(self, *args, before: str = None, after: str = None) -> "tp.tibble":
        """
        Move a column or columns to a new position

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to move

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        
        df.relocate('a', before = 'c')

        df.relocate('b', after = 'c')
        """
        move_cols = pl.Series(list(args))

        if len(move_cols) == 0:
            return self
        else:
            if (before != None) & (after != None):
                raise ValueError("Cannot provide both before and after")

            all_cols = pl.Series(self.columns)
            all_locs = pl.Series(range(len(all_cols)))
            
            move_cols = pl.Series(self.select(move_cols).columns)
            move_locs = all_locs[all_cols.is_in(move_cols)]

            if (before == None) & (after == None):
                before_loc = 0
            elif before != None:
                before = self.select(before).columns[0]
                before_loc = all_locs[all_cols == before][0]
            else:
                after = self.select(after).columns[0]
                before_loc = all_locs[all_cols == after][0] + 1

            before_locs = pl.Series(range(before_loc))
            after_locs = pl.Series(range(before_loc, len(all_cols)))

            before_locs = before_locs[~before_locs.is_in(move_locs)]
            after_locs = after_locs[~after_locs.is_in(move_locs)]

            final_order = before_locs.cast(int)
            final_order.append(move_locs.cast(int))
            final_order.append(after_locs.cast(int))

            ordered_cols = all_cols.take(final_order)

            return self.select(ordered_cols)
    
    def select(self, *args) -> "tp.tibble":
        """
        Select or drop columns

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to select

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        
        df.select('a', 'b')

        df.select(col('a'), col('b'))
        """
        args = args_as_list(args)
        return super().select(args).pipe(as_tibble)
    
    def summarize(self, *args, **kwargs) -> "tp.tibble":
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        
        df.summarize(avg_a = col('a').mean())

        df.summarize(avg_a = col('a').mean(),
                     max_b = col('b').max()))
        """
        exprs = args_as_list(args) + kwargs_as_exprs(kwargs)
        return super().select(exprs).pipe(as_tibble)

class grouped_tibble(pl.eager.frame.GroupBy):
    def filter(self, *args) -> "tp.tibble":
        """
        Filter rows on one or more conditions by group

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        
        df.group_by('b').filter(col('a') < col('a').mean())
        """
        args = args_as_list(args)
        exprs = ft.reduce(lambda a, b: a & b, args)
        return self.apply(lambda df: df.filter(exprs)).pipe(as_tibble)
    
    def mutate(self, *args, **kwargs) -> "tp.tibble":
        """
        Add or modify columns by group

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        
        df.group_by('b').mutate(avg_a = col('a').mean())
        """
        exprs = args_as_list(args) + kwargs_as_exprs(kwargs)
        return self.apply(lambda df: df.with_columns(exprs)).pipe(as_tibble)

    def summarize(self, *args, **kwargs) -> "tp.tibble":
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Examples
        --------
        df = tp.tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        
        df.summarize(avg_a = col('a').mean())

        df.group_by('c').summarize(avg_a = col('a').mean(),
                                   max_b = col('b').max())
        """
        exprs = args_as_list(args) + kwargs_as_exprs(kwargs)
        return self.agg(exprs).pipe(as_tibble)

