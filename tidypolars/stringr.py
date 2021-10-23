from tidypolars import col
import polars as pl
import functools as ft
from .utils import _col_expr
from .funs import is_not

__all__ = [
    "str_detect", 
    "str_length",
    "str_remove_all",
    "str_remove", 
    "str_replace_all", 
    "str_replace", 
    "str_sub",
    "str_to_lower", 
    "str_to_upper"
]

def str_detect(string : str, pattern : str, negate: bool = False):
    """
    Detect the presence or absence of a pattern in a string

    Parameters
    ----------
    string : str
        Input series to operate on
    pattern : str
        Pattern to look for
    negate : bool
        If True, return non-matching elements

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_detect('name', ['a']))
    >>> df.mutate(x = str_detect('name', ['a', 'e']))
    """
    if isinstance(pattern, str):
        pattern = [pattern]
    
    string = _col_expr(string)

    exprs = (string.str.contains(p) for p in pattern)
    exprs = ft.reduce(lambda a, b : a & b, exprs)
    if negate:
        exprs = exprs.is_not()
    
    return exprs

def str_length(string : str):
    """
    Length of a string

    Parameters
    ----------
    string : str
        Input series to operate on

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_length(col('name')))
    """
    string = _col_expr(string)
    return string.str.lengths()

def str_sub(string : str, start : int = 0, end : int = None):
    """
    Extract portion of string based on start and end inputs

    Parameters
    ----------
    string : str
        Input series to operate on
    start : int
        First position of the character to return
    end : int
        Last position of the character to return

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_sub(col('name'), 0, 3))
    """
    string = _col_expr(string) 
    return string.str.slice(start, end)

def str_remove_all(string : str, pattern : str):
    """
    Removes all matched patterns in a string

    Parameters
    ----------
    string : str
        Input series to operate on
    pattern : str
        Pattern to look for

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_remove_all(col('name'), 'a'))
    """
    return str_replace_all(string, pattern, "")

def str_remove(string : str, pattern : str):
    """
    Removes the first matched patterns in a string

    Parameters
    ----------
    string : str
        Input series to operate on
    pattern : str
        Pattern to look for

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_remove(col('name'), 'a'))
    """
    return str_replace(string, pattern, "")

def str_replace_all(string : str, pattern : str, replacement : str):
    """
    Replaces all matched patterns in a string

    Parameters
    ----------
    string : str
        Input series to operate on
    pattern : str
        Pattern to look for
    replacement : str
        String that replaces anything that matches the pattern

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_replace_all(col('name'), 'a', 'A'))
    """
    string = _col_expr(string)
    return string.str.replace_all(pattern, replacement)

def str_replace(string : str, pattern : str, replacement : str):
    """
    Replaces the first matched patterns in a string

    Parameters
    ----------
    string : str
        Input series to operate on
    pattern : str
        Pattern to look for
    replacement : str
        String that replaces anything that matches the pattern

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_replace(col('name'), 'a', 'A'))
    """
    string = _col_expr(string)
    return string.str.replace(pattern, replacement)

def str_to_lower(string : str):
    """
    Convert case of a string

    Parameters
    ----------
    string : str
        Convert case of this string

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_to_lower(col('name')))
    """
    string = _col_expr(string)
    return string.str.to_lowercase()

def str_to_upper(string : str):
    """
    Convert case of a string

    Parameters
    ----------
    string : str
        Convert case of this string

    Examples
    --------
    >>> df = tp.Tibble(name = ['apple', 'banana', 'pear', 'grape'])
    >>> df.mutate(x = str_to_upper(col('name')))
    """
    string = _col_expr(string)
    return string.str.to_uppercase()
