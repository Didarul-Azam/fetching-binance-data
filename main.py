from fastapi import FastAPI, Path
import pandas as pd

app = FastAPI()

@app.get("/")
def index():
    return {'To see latest BTC price':'go to "/BTC-USDT"'
            
            }
@app.get("/BTC-USDT")
def btcprice(n:int|None=5):
    df = pd.read_csv('Kline.csv')
    df = df.set_index('Close time')
    df = df.astype(str)
    if n>0:
        df1 = df.tail(n)
        dic = {'BTC-USDT price': df1['close']}
        return dic 
    return {'query value error':'plz provide n>0'}
  
@app.get("/BTC-USDT/All_indicators")
def all_indicators(n:int|None=5):
    df = pd.read_csv('Kline.csv')
    df = df.set_index('Close time')
    df = df.astype(str)
    if n>0:
        df1 = df.tail(n)
        dic = {'Price':df1['close'],
               'RSI':df1['RSI'],
               'MACD':{'MACD':df1['MACD'],'Signal':df1['MACD Signal'],'MACD histogram':df1["MACD histogram"]},
               'Stochastic':{'Fast stochastic':df1['Fast Stochastic'],'Slow Stochastic':df1['Slow Stochastic']},
               'EMA':df1['EMA'],'SMA':df1['SMA'],
               'A/D Line':df1['A/D Line'],
               'OBV':df1['OBV'],'CMF':df1['CMF'],
               'MFI':df1['MFI']}
        return dic
    return {'query value error':'plz provide n>0'}

@app.get("/BTC-USDT/indicator/{indicator_name}")
def indicator(indicator_name:str = Path(description='Choose from: RSI,MACD,Stochastic,EMA,SMA,A/D Line,OBV,MFI,CMF'),n:int|None=5):
    df = pd.read_csv('Kline.csv')
    df = df.set_index('Close time')
    df = df.astype(str)
    if n>0:
        df1 = df.tail(n)
        if indicator_name not in ['MACD','Stochastic']:    
            dic = {'Price':df1['close'],
                  indicator_name: df1[indicator_name]}
            return dic
        elif indicator_name == 'MACD':
            dic = {'Price': df1['close'],
                   'MACD':{'MACD':df1['MACD'],'Signal':df1['MACD Signal'],'MACD histogram':df1["MACD histogram"]}}
            return dic
        elif indicator_name == 'Stochastic':
            dic = {'Price':df1['close'],
                   'Stochastic':{'Fast stochastic':df1['Fast Stochastic'],'Slow Stochastic':df1['Slow Stochastic']}}
            return dic    
    return {'query value error':'plz provide n>0'}