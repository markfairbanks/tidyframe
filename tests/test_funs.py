import tidypolars as tp
from tidypolars import col

def test_lag():
    """Can get lagging values with function"""
    df = tp.Tibble({'x': range(3)})
    actual = df.mutate(lag_fun = tp.lag(col('x')),
                       lag_mth = col('x').lag(1, default = 1))
    expected = tp.Tibble({'x': range(3),
                          'lag_fun': [None, 0, 1],
                          'lag_mth': [1, 0, 1]})
    assert actual.frame_equal(expected, null_equal = True), "lag failed"

def test_lead():
    """Can get leading values with function"""
    df = tp.Tibble({'x': range(3)})
    actual = df.mutate(lead_fun = tp.lead(col('x')),
                       lead_mth = col('x').lead(1, default = 1))
    expected = tp.Tibble({'x': range(3),
                          'lead_fun': [1, 2, None],
                          'lead_mth': [1, 2, 1]})
    assert actual.frame_equal(expected, null_equal = True), "lead failed"