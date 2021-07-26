# -*- coding: utf-8 -*-
import pandas_ta
from numpy import nan as npNaN
from pandas import DataFrame
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, verify_series
from pandas_ta.overlap import vidya



def pmax(high, low, close, length=None, multiplier=None, offset=None, **kwargs):
    """Indicator: PMAX"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 7
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 3.0
    close = verify_series(close, length)
    offset = get_offset(offset)

    if high is None or low is None or close is None: return

    # Calculate Results
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [npNaN] * m, [npNaN] * m

    vidya_ = vidya(close, length=10)
    matr = multiplier * atr(high, low, close, length)
    upperband = vidya_ + matr
    lowerband = vidya_ - matr

    for i in range(1, m):
        if close.iloc[i] > upperband.iloc[i - 1]:
            dir_[i] = 1
        elif close.iloc[i] < lowerband.iloc[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lowerband.iloc[i]
        else:
            trend[i] = short[i] = upperband.iloc[i]

    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
            f"SUPERT{_props}": trend,
            f"SUPERTd{_props}": dir_,
            f"SUPERTl{_props}": long,
            f"SUPERTs{_props}": short,
        }, index=close.index)

    df.name = f"SUPERT{_props}"
    df.category = "overlap"

    # Apply offset if needed
    if offset != 0:
        df = df.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    if "fill_method" in kwargs:
        df.fillna(method=kwargs["fill_method"], inplace=True)

    return df


pmax.__doc__ = \
"""PMAX (eke-edit)



Sources:
    https://www.onbirkod.com/profit-maximizer-pmax-supertrendin-bir-tik-otesi-python-ile-yazalim/
    https://tr.tradingview.com/script/sU9molfV/#:~:text=Profit%20Maximizer%20%2D%20PMax%20tries%20to,its%20ancestors%20MOST%20and%20SuperTrend.

Calculation:
    Default Inputs:
        length=7, multiplier=3.0
    Default Direction:
	Set to +1 or bullish trend at start

    MID = multiplier * ATR
    LOWERBAND = vidya - MID
    UPPERBAND = vidya + MID

    if UPPERBAND[i] < FINAL_UPPERBAND[i-1] and close[i-1] > FINAL_UPPERBAND[i-1]:
        FINAL_UPPERBAND[i] = UPPERBAND[i]
    else:
        FINAL_UPPERBAND[i] = FINAL_UPPERBAND[i-1])

    if LOWERBAND[i] > FINAL_LOWERBAND[i-1] and close[i-1] < FINAL_LOWERBAND[i-1]:
        FINAL_LOWERBAND[i] = LOWERBAND[i]
    else:
        FINAL_LOWERBAND[i] = FINAL_LOWERBAND[i-1])

    if close[i] <= FINAL_UPPERBAND[i]:
        SUPERTREND[i] = FINAL_UPPERBAND[i]
    else:
        SUPERTREND[i] = FINAL_LOWERBAND[i]

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int) : length for ATR calculation. Default: 7
    multiplier (float): Coefficient for upper and lower band distance to
        midrange. Default: 3.0
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: SUPERT (trend), SUPERTd (direction), SUPERTl (long), SUPERTs (short) columns.
"""
