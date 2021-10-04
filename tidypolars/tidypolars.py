import polars as pl
import functools as ft

from typing import Union, List

col = pl.col

def as_tidyframe(df):
    df.__class__ = tidyframe
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
    if isinstance(x, list):
        return x[0]
    elif is_list_like(x[0]):
        return list(x[0])
    else:
        return [*x]

def as_series(x):
    if isinstance(pl.Series):
        return x
    else:
        return pl.Series(as_list(x))

# Convert kwargs to col() expressions with alias
def kwargs_as_exprs(kwargs):
    return [expr.alias(key) for key, expr in kwargs.items()]

class tidyframe(pl.DataFrame):
    def arrange(self, *args, desc: Union[bool, List[bool]] = False) -> "tp.tidyframe":
        """
        Arrange/sort rows

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to sort by

        desc : Union[bool, List[bool]] = False
            Should columns be ordered in descending order

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe({'x': ['a', 'a', 'b'], 'y': range(3)})
        
        # Arrange in ascending order
        df.arrange('x', 'y')
        
        # Arrange some columns descending
        df.arrange('x', 'y', desc = [True, False])
        """
        exprs = as_list(args)
        return self.sort(exprs, reverse = desc).pipe(as_tidyframe)
    
    def filter(self, *args) -> "tp.tidyframe":
        """
        Filter rows on one or more conditions

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.filter(col('a') < 2, col('c') == 'a')

        df.filter((col('a') < 2) & (col('c') == 'a'))
        """
        args = list(args)
        exprs = ft.reduce(lambda a, b: a & b, args)
        return super().filter(exprs).pipe(as_tidyframe)
    
    def group_by(df, *args):
        """
        Group by one or more variables

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        Returns
        -------
        tf.grouped_tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.group_by('c')

        df.group_by('a', 'c')
        """
        args = as_list(args)
        df = df.groupby(args)
        df.__class__ = grouped_tidyframe
        return df
    
    def mutate(self, *args, **kwargs) -> "tp.tidyframe":
        """
        Add or modify columns

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        (
            df
            .mutate(double_a = col('a') * 2,
                    a_plus_b = col('a') + col('b'))
        )
        """
        exprs = list(args) + kwargs_as_exprs(kwargs)
        return self.with_columns(exprs).pipe(as_tidyframe)
    
    def pipe(self, fn, *args, **kwargs):
        """
        Apply a function to the data frame

        Parameters
        ----------
        *args :
            args to pass to the function
        
        **kwargs :
            keyword arguments to pass to the function

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.pipe(print)
        """
        return fn(self, *args, **kwargs)
    
    def relocate(self, *args, before: str = None, after: str = None) -> "tp.tidyframe":
        """
        Move a column or columns to a new position

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to move

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
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
    
    def select(self, *args) -> "tp.tidyframe":
        """
        Select or drop columns

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to select

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.select('a', 'b')

        df.select(col('a'), col('b'))
        """
        args = args_as_list(args)
        return super().select(args).pipe(as_tidyframe)
    
    def summarize(self, *args, **kwargs) -> "tp.tidyframe":
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.summarize(avg_a = col('a').mean())

        (
            df
            .summarize(avg_a = col('a').mean(),
                       max_b = col('b').max())
        )
        """
        exprs = list(args) + kwargs_as_exprs(kwargs)
        return super().select(exprs).pipe(as_tidyframe)

class grouped_tidyframe(pl.eager.frame.GroupBy):
    def filter(self, *args) -> "tp.tidyframe":
        """
        Filter rows on one or more conditions by group

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.group_by('c').filter(col('a') < col('a').mean())
        """
        args = list(args)
        exprs = ft.reduce(lambda a, b: a & b, args)
        return self.apply(lambda df: df.filter(exprs)).pipe(as_tidyframe)
    
    def mutate(self, *args, **kwargs) -> "tp.tidyframe":
        """
        Add or modify columns by group

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.mutate(avg_a = col('a').mean())
        """
        exprs = list(args) + kwargs_as_exprs(kwargs)
        return self.apply(lambda df: df.with_columns(exprs)).pipe(as_tidyframe)

    def summarize(self, *args, **kwargs) -> "tp.tidyframe":
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        **kwargs : Expr
            Column expressions to add or modify

        Returns
        -------
        tp.tidyframe

        Examples
        --------
        df = tp.tidyframe(
            {'a': range(3),
             'b': range(3),
             'c': ['a', 'a', 'b']}
        )
        
        df.summarize(avg_a = col('a').mean())

        (
            df
            .group_by('c')
            .summarize(avg_a = col('a').mean(),
                       max_b = col('b').max())
        )
        """
        exprs = list(args) + kwargs_as_exprs(kwargs)
        return self.agg(exprs).pipe(as_tidyframe)

