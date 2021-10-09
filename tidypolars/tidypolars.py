import polars as pl
import functools as ft
from typing import Dict, List, Union

__all__ = [
    "Tibble",
    "from_pandas", "from_polars"
    # reexports
    "col", "Expr", "Series",
]

# reexports
col = pl.col
Expr = pl.Expr
Series = pl.Series
  
def _is_list_like(x):
    if isinstance(x, list) | isinstance(x, pl.Series):
        return True
    else:
        return False

def _as_list(x):
    if isinstance(x, list):
        return x.copy()
    elif isinstance(x, str):
        return [x]
    else:
        return list(x)

def _args_as_list(x):
    if len(x) == 0:
        return []
    elif isinstance(x[0], list):
        return x[0]
    elif isinstance(x[0], pl.Series):
        return list(x[0])
    else:
        return [*x]

def from_polars(df):
    df.__class__ = Tibble
    return df

def from_pandas(df):
    return from_pandas(pl.from_pandas(df))

# Convert kwargs to col() expressions with alias
def _kwargs_as_exprs(kwargs):
    return [expr.alias(key) for key, expr in kwargs.items()]

def _no_groupby(gb):
    if isinstance(gb, Expr) | isinstance(gb, str) | isinstance(gb, list):
        return False
    else:
        return True

class Tibble(pl.DataFrame):
    def __repr__(self) -> str:
        df = self.to_polars()
        return df.__str__()

    def arrange(self, *args, desc: bool = False):
        """
        Arrange/sort rows

        Parameters
        ----------
        *args : 
            Columns to sort by
        desc : 
            Should columns be ordered in descending order

        Examples
        --------
        >>> df = tp.Tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        >>> # Arrange in ascending order
        >>> df.arrange('x', 'y')
        ...
        >>> # Arrange some columns descending
        >>> df.arrange('x', 'y', desc = [True, False])
        """
        exprs = _args_as_list(args)
        return self.sort(exprs, reverse = desc).pipe(from_polars)

    def bind_cols(self, df: "tp.Tibble"):
        """
        Bind data frames by columns

        Parameters
        ----------
        df : Tibble
            Data frame to bind

        Examples
        --------
        >>> df1 = tp.Tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        >>> df2 = tp.Tibble({'a': ['c', 'c', 'c'], 'b': range(4, 7)})
        >>> df1.bind_cols(df2)
        """
        return self.hstack(df).pipe(from_polars)
    
    def bind_rows(self, df: "tp.Tibble"):
        """
        Bind data frames by row

        Parameters
        ----------
        df : Tibble
            Data frame to bind

        Examples
        --------
        >>> df1 = tp.Tibble({'x': ['a', 'a', 'b'], 'y': range(3)})
        >>> df2 = tp.Tibble({'x': ['c', 'c', 'c'], 'y': range(4, 7)})
        >>> df1.bind_rows(df2)
        """
        return self.vstack(df).pipe(from_polars)

    def distinct(self, *args):
        """
        Select distinct/unique rows

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to find distinct/unique rows

        Examples
        --------
        >>> df = tp.tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        >>> df.distinct()
        >>> df.distinct('b')
        """
        # TODO: Create for series
        args = _args_as_list(args)

        if len(args) == 0:
            df = self.drop_duplicates()
        else:
            df = self.select(args).drop_duplicates()
        
        return df.pipe(from_polars)
    
    def head(self, n = 5, *args, groupby = None):
        """Alias for `.slice_head()`"""
        return self.slice_tail(n, groupby = groupby)

    def filter(self, *args,
               groupby: Union[str, Expr, List[str], List[Expr]] = None):
        """
        Filter rows on one or more conditions

        Parameters
        ----------
        *args : Expr
            Conditions to filter by

        groupby : Union[str, Expr, List[str], List[Expr]]
            Columns to group by

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': ['a', 'a', 'b']})
        >>> df.filter(col('a') < 2, col('c') == 'a')
        >>> df.filter((col('a') < 2) & (col('c') == 'a'))
        >>> df.filter(col('a') <= col('a').mean(),
        ...           groupby = 'b')
        """
        args = _args_as_list(args)
        exprs = ft.reduce(lambda a, b: a & b, args)

        if _no_groupby(groupby):
            out = super().filter(exprs)
        else:
            out = super().groupby(groupby).apply(lambda x: x.filter(exprs))
        
        return out.pipe(from_polars)

    def mutate(self, *args,
               groupby: Union[str, Expr, List[str], List[Expr]] = None,
               **kwargs):
        """
        Add or modify columns

        Parameters
        ----------
        *args : Expr
            Column expressions to add or modify

        groupby : Union[str, Expr, List[str], List[Expr]]
            Columns to group by
        
        **kwargs : Expr
            Column expressions to add or modify

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3)})
        >>> df.mutate(double_a = col('a') * 2,
        ...           a_plus_b = col('a') + col('b'))
        >>> df.mutate((col(['a', 'b]) * 2).prefix('double_'),
        ...           a_plus_b = col('a') + col('b'))
        """
        exprs = _args_as_list(args) + _kwargs_as_exprs(kwargs)
        if _no_groupby(groupby):
            out = self.with_columns(exprs)
        else:
            out = self.groupby(groupby).apply(lambda x: x.with_columns(exprs))
        
        return out.pipe(from_polars)

    def pull(self, var: str = None):
        """
        Extract a column as a series

        Parameters
        ----------
        var : str
            Name of the column to extract. Defaults to the last column.

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3))
        >>> df.pull('a')
        """
        if var == None:
            var = self.columns[-1]
        
        return self.get_column(var)
    
    def relocate(self, *args, before: str = None, after: str = None):
        """
        Move a column or columns to a new position

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to move

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.relocate('a', before = 'c')
        >>> df.relocate('b', after = 'c')
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
    
    def rename(self, mapping: Dict[str, str]):
        """
        Rename columns

        Parameters
        ----------
        *args : Dict[str, str]
            Dictionary mapping of new names

        Examples
        --------
        >>> df = tp.Tibble({'x': range(3), 't': range(3), 'z': ['a', 'a', 'b']})
        >>> df.rename({'x': 'new_x'})
        """
        return super().rename(mapping).pipe(from_polars)
    
    def select(self, *args):
        """
        Select or drop columns

        Parameters
        ----------
        *args : Union[str, Expr]
            Columns to select

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.select('a', 'b')
        >>> df.select(col('a'), col('b'))
        """
        args = _args_as_list(args)
        return super().select(args).pipe(from_polars)

    def slice(self, *args, groupby = None):
        """
        Grab rows from a data frame

        Parameters
        ----------
        *args : Union[int, List[int]]
            Rows to grab
        
        groupby : Union[str, Expr, List[str], List[Expr]]
            Columns to group by

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.slice(0, 1)
        >>> df.slice(0, groupby = 'c')
        """
        rows = _args_as_list(args)
        if _no_groupby(groupby):
            df = self[rows]
        else:
            df = self.groupby(groupby).apply(lambda x: x[rows])
        return df.pipe(from_polars)

    def slice_head(self, n: int = 5, *args, groupby = None):
        """
        Grab top rows from a data frame

        Parameters
        ----------
        n : int
            Number of rows to grab
        
        *args :
            Currently unused
        
        groupby : Union[str, Expr, List[str], List[Expr]]
            Columns to group by

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.slice_head(2)
        >>> df.slice_head(1, groupby = 'c')
        """
        args = _args_as_list(args)
        col_order = super().columns
        if _no_groupby(groupby):
            df = super().head(n)
        else:
            df = super().groupby(groupby).head(n)
        return df.pipe(from_polars).select(col_order)

    def slice_tail(self, n: int = 5, *args, groupby = None):
        """
        Grab bottom rows from a data frame

        Parameters
        ----------
        n : int
            Number of rows to grab
        
        *args :
            Currently unused
        
        groupby : Union[str, Expr, List[str], List[Expr]]
            Columns to group by

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.slice_tail(2)
        >>> df.slice_tail(1, groupby = 'c')
        """
        args = _args_as_list(args)
        col_order = super().columns
        if _no_groupby(groupby):
            df = super().tail(n)
        else:
            df = super().groupby(groupby).tail(n)
        return df.pipe(from_polars).select(col_order)
    
    def summarize(self, *args,
                  groupby: Union[str, Expr, List[str], List[Expr]] = None,
                  **kwargs):
        """
        Aggregate data with summary statistics

        Parameters
        ----------
        *args : Expr

        groupby : Union[str, Expr, List[str], List[Expr]]
            Columns to group by

        **kwargs : Expr
            Column expressions to add or modify

        Examples
        --------
        >>> df = tp.Tibble({'a': range(3), 'b': range(3), 'c': ['a', 'a', 'b']})
        >>> df.summarize(avg_a = col('a').mean())
        >>> df.summarize(avg_a = col('a').mean(),
        ...              groupby = 'c')
        >>> df.summarize(avg_a = col('a').mean(),
        ...              max_b = col('b').max())
        """
        exprs = _args_as_list(args) + _kwargs_as_exprs(kwargs)

        if _no_groupby(groupby):
            out = super().select(exprs)
        else:
            out = super().groupby(groupby).agg(exprs)
        
        return out.pipe(from_polars)

    def tail(self, n = 5, *args, groupby = None):
        """Alias for `.slice_tail()`"""
        return self.slice_tail(n, groupby = groupby)

    def to_polars(self):
        """
        Convert to a polars DataFrame

        Examples
        --------
        >>> df.to_pandas()
        """
        return super().to_pandas()

    def to_polars(self):
        """
        Convert to a polars DataFrame

        Examples
        --------
        >>> df.to_polars()
        """
        self.__class__ = pl.DataFrame
        return self