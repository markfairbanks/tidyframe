import polars as pl
from .tidypolars import from_polars
from .utils import _col_expr

__all__ = [
    "abs",
    "case_when", "if_else",
    "lag", "lead",
    "read_csv", "read_parquet",
    "round",

    # agg stats
    "first", "last",
    "max", "mean", "median", "min",
    "n_distinct", "sd", "sum",

    # predicates
    "between", "is_finite", "is_in", "is_infinite",
    "is_nan", "is_not", "is_not_in", "is_not_null", "is_null"
]

def abs(x):
    """
    Absolute value

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.mutate(abs_x = tp.abs('x'))
    >>> df.mutate(abs_x = tp.abs(col('x')))
    """
    x = _col_expr(x)
    return x.abs()

def between(x, left, right):
    """
    Test if values of a column are between two values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    left : int
        Value to test if column is greater than or equal to
    right : int
        Value to test if column is less than or equal to

    Examples
    --------
    >>> df = tp.Tibble(x = range(4))
    >>> df.filter(tp.between(col('x'), 1, 3))
    """
    x = _col_expr(x)
    return (x >= left) & (x <= right)

def case_when(expr):
    """
    Case when

    Parameters
    ----------
    expr : Expr
        A logical expression

    Examples
    --------
    >>> df = tp.Tibble(x = range(1, 4))
    >>> df.mutate(
    >>>    case_x = tp.case_when(col('x') < 2).then(1)
    >>>             .when(col('x') < 3).then(2)
    >>>             .otherwise(0)
    >>> )
    """
    return pl.when(expr)

def first(x):
    """
    Get first value

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(first_x = tp.first('x'))
    >>> df.summarize(first_x = tp.first(col('x')))
    """
    x = _col_expr(x)
    return x.first()

def if_else(condition, true, false):
    """
    If Else

    Parameters
    ----------
    condition : Expr
        A logical expression
    true :
        Value if the condition is true
    false :
        Value if the condition is false

    Examples
    --------
    >>> df = tp.Tibble(x = range(1, 4))
    >>> df.mutate(if_x = tp.if_else(col('x') < 2, 1, 2))
    """
    return pl.when(condition).then(true).otherwise(false)

def is_finite(x):
    """
    Test if values of a column are finite

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.Tibble(x = [1.0, float('inf')])
    >>> df.filter(tp.is_finite(col('x')))
    """
    x = _col_expr(x)
    return x.is_finite()

def is_in(x, y):
    """
    Test if values of a column are in a list of values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    y : list
        List to test against

    Examples
    --------
    >>> df = tp.Tibble(x = range(3))
    >>> df.filter(tp.is_in(col('x'), [1, 2]))
    """
    x = _col_expr(x)
    return x.is_in(y)

def is_infinite(x):
    """
    Test if values of a column are infinite

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.Tibble(x = [1.0, float('inf')])
    >>> df.filter(tp.is_infinite(col('x')))
    """
    x = _col_expr(x)
    return x.is_infinite()

def is_not(x):
    """
    Flip values of a boolean series

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.Tibble(x = range(3))
    >>> df.filter(tp.is_not(col('x') < 2))
    """
    x = _col_expr(x)
    return x.is_not()

def is_nan(x):
    """
    Test if values of a column are nan

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.Tibble(x = range(3))
    >>> df.filter(tp.is_nan(col('x')))
    """
    x = _col_expr(x)
    return x.is_nan()

def is_not_in(x, y):
    """
    Test if values of a column are not in a list of values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    y : list
        List to test against

    Examples
    --------
    >>> df = tp.Tibble(x = range(3))
    >>> df.filter(tp.is_not_in(col('x'), [1, 2]))
    """
    x = _col_expr(x)
    return x.is_in(y).is_not()

def is_not_null(x):
    """
    Test if values of a column are not null

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.Tibble(x = range(3))
    >>> df.filter(tp.is_not_in(col('x'), [1, 2]))
    """
    x = _col_expr(x)
    return x.is_null().is_not()

def is_null(x):
    """
    Test if values of a column are null

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df = tp.Tibble(x = range(3))
    >>> df.filter(tp.is_not_in(col('x'), [1, 2]))
    """
    x = _col_expr(x)
    return x.is_null()

def _shift(x, n, default):
    if default == None:
        return x.shift(n)
    else:
        return x.shift_and_fill(n, default)

def lag(x, n: int = 1, default = None):
    """
    Get lagging values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    n : int
        Number of positions to lag by

    default : optional
        Value to fill in missing values

    Examples
    --------
    >>> df.mutate(lag_x = tp.lag(col('x')))
    >>> df.mutate(lag_x = tp.lag('x'))
    """
    x = _col_expr(x)
    return _shift(x, n, default)

def last(x):
    """
    Get last value

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(last_x = tp.last('x'))
    >>> df.summarize(last_x = tp.last(col('x')))
    """
    x = _col_expr(x)
    return x.last()

def lead(x, n: int = 1, default = None):
    """
    Get leading values

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    n : int
        Number of positions to lead by

    default : optional
        Value to fill in missing values

    Examples
    --------
    >>> df.mutate(lead_x = tp.lead(col('x')))
    >>> df.mutate(lead_x = col('x').lead())
    """
    x = _col_expr(x)
    return _shift(x, -n, default)

def max(x):
    """
    Get column max

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(max_x = tp.max('x'))
    >>> df.summarize(max_x = tp.max(col('x')))
    """
    x = _col_expr(x)
    return x.max()

def mean(x):
    """
    Get column mean

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(mean_x = tp.mean('x'))
    >>> df.summarize(mean_x = tp.mean(col('x')))
    """
    x = _col_expr(x)
    return x.mean()

def median(x):
    """
    Get column median

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(median_x = tp.median('x'))
    >>> df.summarize(median_x = tp.median(col('x')))
    """
    x = _col_expr(x)
    return x.median()

def min(x):
    """
    Get column minimum

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(min_x = tp.min('x'))
    >>> df.summarize(min_x = tp.min(col('x')))
    """
    x = _col_expr(x)
    return x.min()

def n_distinct(x):
    """
    Get number of distinct values in a column

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(min_x = tp.n_distinct('x'))
    >>> df.summarize(min_x = tp.n_distinct(col('x')))
    """
    x = _col_expr(x)
    return x.n_unique()

def read_csv(file: str,
             *args,
             **kwargs):
    """Simple wrapper around polars.read_csv"""
    return pl.read_csv(file, *args, **kwargs).pipe(from_polars)

def read_parquet(source: str,
                 *args,
                 **kwargs):
    """Simple wrapper around polars.read_parquet"""
    return pl.read_parquet(source, *args, **kwargs).pipe(from_polars)

def round(x, decimals = 0):
    """
    Get column standard deviation

    Parameters
    ----------
    x : Expr, Series
        Column to operate on
    decimals : int
        Decimals to round to

    Examples
    --------
    >>> df.mutate(x = tp.round(col('x')))
    """
    x = _col_expr(x)
    return x.round(decimals)

def sd(x):
    """
    Get column standard deviation

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(sd_x = tp.sd('x'))
    >>> df.summarize(sd_x = tp.sd(col('x')))
    """
    x = _col_expr(x)
    return x.std()

def sum(x):
    """
    Get column sum

    Parameters
    ----------
    x : Expr, Series
        Column to operate on

    Examples
    --------
    >>> df.summarize(sum_x = tp.sum('x'))
    >>> df.summarize(sum_x = tp.sum(col('x')))
    """
    x = _col_expr(x)
    return x.sum()
