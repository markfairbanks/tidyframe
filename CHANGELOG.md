# Changelog

## v0.3.2 (in development)

#### Functionality improvements

* `pl.Null` is rexported as `tp.Null`
* `.rename()` `mapping` renamed to `_mapping` to avoid naming conflicts in
    dplyr interface using kwargs

## v0.3.1

#### Functionality improvements

* `if_else()` treats string inputs in `true` and `false` as strings and not as columns
* `case_when()` now has syntax closer to `dplyr::case_when()`

#### New tibble methods

* `.print()`

## v0.3.0

* Major refactor to work with `polars>=1.0.0`

#### Functionality improvements

* Convert `by` arg `_by` to allow naming columns `by` in `.mutate()`/`.summarize()`
* Convert `.to_pandas()`/`.to_polars()` to `.as_pandas()`/`.as_polars()`
* Can extract a column using `df["x"]`

#### New functions

* `as_tibble()`
* `is_tibble()`
* `where()`

## v0.2.19

#### New functions
* `make_date()`
* `make_datetime()`

## v0.2.18

* polars >=0.14.18 compatibility

## v0.2.17 (2022/8/17)

* tidypolars is now compatible with polars >=0.14.0

## v0.2.16 (2022/8/12)

* Require polars <0.14.0

## v0.2.15 (2022/4/22)

* Minor update to `__version__` check

## v0.2.14 (2022/4/22)

* Added support for python 3.7

## v0.2.13 (2022/4/7)

#### New functions

* `cor()`
* `cov()`
* `log()`
* `log10()`
* `rep()`
* `var()`

#### Methods with notable speed improvements

* `.separate()`

## v0.2.12 (2022/3/24)

#### New Tibble methods

* `.unite()`

## v0.2.11 (2022/2/11)

#### New functions

* `across()`
* `as_boolean()`

#### Functionality improvements

* Can pass an empty list to `by`
* `.mutate()`

  * Column expressions are evaluated sequentially in order to match dplyr semantics
  * Can add a new column with a constant without `tp.lit()`

## v0.2.10 (2022/2/7)

#### New Tibble methods

* `.separate()`

#### New functions

* `coalesce()`
* `n()`
* `row_number()`
* `str_c()`
* `str_ends()`
* `str_starts()`

## v0.2.9 (2022/2/6)

#### Bug fixes

* Update `.distinct()` to work with polars >= 0.12.20

## v0.2.8 (2021/12/8)

#### Bug fixes

* Can use `fmt` arg in `as_date()` and `as_datetime()` (#155)

## v0.2.7 (2021/11/19)

#### New Tibble methods

* `.to_dict()`

## v0.2.6 (2021/11/18)

#### New functions

* `count()`
* `floor()`
* `length()`
* `quantile()`
* `sqrt()`

#### Functionality improvements

* `.bind_rows()`: Auto-aligns columns by name

## v0.2.5 (2021/11/16)

## v0.2.4 (2021/11/15)

## v0.2.3 (2021/11/15)

## v0.2.2 (2021/11/15)

#### New functions
* `paste()`
* `paste0()`

#### Improved functionality

* `.relocate()`: tidyselect helpers work

## v0.2.1 (2021/11/8)

#### New Tibble methods

* `.replace_null()`
* `.set_names()`

#### New functions

* `replace_null()`

## v0.2.0 (2021/11/5)

#### New Functions

* `as_float()`
* `as_integer()`
* `as_string()`
* `between()`
* `cast()`
* `desc()`
* `is_finite()`
* `is_in()`
* `is_infinite()`
* `is_not()`
* `is_not_in()`
* `is_not_null()`
* `is_null()`
* `round()`
* `lubridate`
  * `as_date()`
  * `as_datetime()`
  * `dt_round()`
  * `hour()`
  * `mday()`
  * `minute()`
  * `month()`
  * `quarter()`
  * `second()`
  * `wday()`
  * `week()`
  * `yday()`
  * `year()`
* `stringr`
  * `str_detect()`
  * `str_extract()`
  * `str_length()`
  * `str_remove_all()`
  * `str_remove()`
  * `str_replace_all()`
  * `str_replace()`
  * `str_sub()`
  * `str_to_lower()`
  * `str_to_upper()`
  * `str_trim()`

#### Improved functionality

* `.drop()`: tidyselect helpers work

## v0.1.7 (2021/10/20)

#### New Tibble methods

* `.count()`
* `.drop_null()`
* `.inner_join()`/`.left_join()`/`.full_join()`
* `.frame_equal()`
* `.write_csv()`
* `.write_parquet()`

#### New functions

* `abs()`
* `case_when()`
* `first()`
* `if_else()`
* `lag()`
* `last()`
* `lead()`
* `max()`
* `mean()`
* `median()`
* `min()`
* `n_distinct()`
* `read_csv()`
* `read_parquet()`
* `sd()`
* `sum()`
* `tidyselect`
  * `contains()`
  * `ends_with()`
  * `everything()`
  * `starts_with()`

#### Improved functionality

* `.bind_cols()`/`.bind_rows()`: Can append multiple data frames in one call

## v0.1.6 (2021/10/13)

#### Improved functionality

* `.rename()`: Can now use both a dplyr-like and pandas-like interface
  
#### New attributes
* `.names`
* `.ncol`
* `.nrow`

## v0.1.5 (2021/10/12)

#### New Tibble methods

* `.fill()`
* `.head()`
* `.pivot_longer()`
* `.pivot_wider()`
* `.tail()`
* `.slice_head()`
* `.slice_tail()`

## v0.1.4 (2021/10/6)

#### New Tibble methods

* `.bind_cols()`
* `.bind_rows()`
* `.distinct()`
* `.pull()`
* `.rename()`
* `.slice()`

#### Methods with new `by` arg

* `.filter()`
* `.mutate()`
* `.slice()`
* `.summarize()`

#### Miscellaneous

* Class name changed from tibble to Tibble

## v0.1.3 (2021/10/4)

* Class name changed from tidyframe to tibble

## v0.1.2 (2021/10/4)

## v0.1.1 (2021/10/4)

## v0.1.0 (2021/10/2)

* First release of `tidypolars`