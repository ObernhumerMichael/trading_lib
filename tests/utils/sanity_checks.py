import pytest

import pandas as pd

from py_trading_lib.utils.sanity_checks import *


@pytest.fixture
def extended_tohlcv():
    kline = {
        "TIME": [1],
        "OPEN": [1],
        "HIGH": [1],
        "LOW": [1],
        "CLOSE": [1],
        "VOLUME": [1],
        "EXTRA": [1],
    }
    return pd.DataFrame(kline)


def test_check_cols_for_tohlcv_fail(not_kline_data: pd.DataFrame):
    with pytest.raises(ValueError):
        check_cols_for_tohlcv(not_kline_data)


@pytest.mark.parametrize("klines", ["example_klines", "extended_tohlcv"])
def test_check_cols_for_tohlcv_pass(
    example_klines: str, request: pytest.FixtureRequest
):
    klines: pd.DataFrame = request.getfixturevalue(example_klines)

    check_cols_for_tohlcv(klines)


def test_check_has_min_len_fail(insufficient_klines: pd.DataFrame):
    min_len = 99999

    with pytest.raises(ValueError):
        check_has_min_len(insufficient_klines, min_len)


def test_check_has_min_len_pass(example_klines: pd.DataFrame):
    min_len = 10

    check_has_min_len(example_klines, min_len)
