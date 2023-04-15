import requests
import json
import pandas as pd
import numpy as np
import time

def get_bars(symbol,interval='1s'):
    """
        Extract the data from binance api
    """
    rooturl = 'https://api.binance.com/api/v3/klines'
    url = rooturl+'?symbol='+symbol+'&interval='+interval
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            df = pd.DataFrame(data)
            df.columns = ['Open time',
                  'open','high','low','close','volume',
                  'Close time','qav','num_trade',
                  'base_v','quote_v','ignore' ]
            df['Open time'] = pd.to_datetime(df['Open time'],unit = 'ms')
            df['Close time'] = pd.to_datetime(df['Close time'],unit = 'ms')
            df.drop(df.columns[[7,8,9,10,11]],axis =1, inplace=True)
            df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
            return df
        else:
            return {"Error:": f"Request failed with status code {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"Error": f"Request failed with error {str(e)}"}

def rsi(df, n=14):
    """
    Calculate RSI indicator.
    """
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(n).mean()
    avg_loss = loss.rolling(n).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def sma(df, n=20):
    """
    Calculate Simple Moving Average (SMA) indicator for a given DataFrame.
    """
    close = df['close']
    sma = close.rolling(n).mean()
    
    return sma    

def ema(df, n=20):
    """
    Calculate Exponential Moving Average (EMA).
    """
    close = df['close']
    ema = close.ewm(span=n, adjust=False).mean()
    
    return ema

def macd(df, n_fast=12, n_slow=26, n_signal=9):
    """
    Calculate Moving Average Convergence Divergence (MACD).
    """
    close = df['close']
    ema_fast = close.ewm(span=n_fast, adjust=False).mean()
    ema_slow = close.ewm(span=n_slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=n_signal, adjust=False).mean()
    histogram = macd - signal
    
    return macd,signal,histogram

def stochastic(df, n=14, d=3):
    """
    Calculate Stochastic Oscillator indicator.
    """
    high = df['high']
    low = df['low']
    close = df['close']
    lowest_low = low.rolling(n).min()
    highest_high = high.rolling(n).max()
    stoch_k = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    stoch_d = stoch_k.rolling(d).mean()
    
    return (stoch_k,stoch_d)

def ad_line(df):
    """
    Calculate Accumulation/Distribution Line indicator.
    """
    high = df['high']
    low = df['low']
    close = df['close']
    volume = df['volume']
    ad = ((close - low) - (high - close)) / (high - low) * volume
    ad_line = ad.cumsum()
    return ad_line

def obv(df):
    """
    Calculate On-Balance Volume (OBV) indicator for a given DataFrame.
    """
    close = df['close']
    volume = df['volume']
    prev_close = close.shift(1)
    obv = pd.Series(0, index=df.index)
    obv[(close >= prev_close)] = volume[(close >= prev_close)]
    obv[(close < prev_close)] = -volume[(close < prev_close)]
    obv = obv.cumsum()
    return obv

def money_flow_index(df, n=14):
    """
    Calculate Money Flow Index (MFI) indicator for a given DataFrame.
    """
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    money_flow = typical_price * df['volume']
    pos_flow = pd.Series(0, index=df.index)
    neg_flow = pd.Series(0, index=df.index)
    pos_flow[typical_price > typical_price.shift(1)] = money_flow[typical_price > typical_price.shift(1)]
    neg_flow[typical_price < typical_price.shift(1)] = money_flow[typical_price < typical_price.shift(1)]
    pos_mf = pos_flow.rolling(n, min_periods=0).sum()
    neg_mf = neg_flow.rolling(n, min_periods=0).sum()
    mfi = 100 - (100 / (1 + (pos_mf / neg_mf)))
    return mfi

def chaikin_money_flow(df, period=20):
    """Calculate Chaikin Money Flow (CMF) for a given period."""
    mfv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
    mfv *= df['volume']
    cmf = mfv.rolling(period).mean() / df['volume'].rolling(period).sum()
    return cmf

def aroon(df, n=25):
    """
    Calculate Aroon Up and Aroon Down.
    """
    high = df['high']
    low = df['low']
    
    up = ((n - (high.rolling(n).apply(lambda x: x.argmax(), raw=True))) / n) * 100
    down = ((n - (low.rolling(n).apply(lambda x: x.argmin(), raw=True))) / n) * 100
    
    return up-down
while True:
    sym = "BTCUSDT"
    klinedf = get_bars(sym.upper())
    klinedf['RSI'] = rsi(klinedf)
    klinedf['CMF'] = chaikin_money_flow(klinedf)
    klinedf['MFI'] = money_flow_index(klinedf)
    c,d,e = macd(klinedf)
    klinedf['MACD'] = c
    klinedf['MACD Signal']=d
    klinedf["MACD histogram"]=e
    klinedf['OBV'] = obv(klinedf)
    klinedf['A/D Line'] = ad_line(klinedf)
    a,b = stochastic(klinedf)
    klinedf['Fast Stochastic'] = a
    klinedf['Slow Stochastic'] = b
    klinedf['SMA'] = sma(klinedf)
    klinedf['EMA'] = ema(klinedf)
    klinedf['Aroon'] = aroon(klinedf)
    data_df = klinedf[['Close time','close','RSI','CMF','MFI','MACD','MACD Signal','MACD histogram','OBV','A/D Line','Fast Stochastic','Slow Stochastic','EMA','SMA','Aroon']]
    data_df.to_csv("Kline.csv",index=False)
    time.sleep(1)
    

