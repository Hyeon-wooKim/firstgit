import pyupbit
import pandas
import datetime
import time

access = "8qdX959Qzsfnr9RkusRsTQzhAfBCx518l6VlhIiI"          # 본인 값으로 변경
secret = "ToqSILTdJOxeMpYM9d9PJ5ZbAxjyOOkec3VpdN28"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

def rsi(ohlc: pandas.DataFrame, period: int = 14):
    delta = ohlc["close"].diff()
    ups, downs = delta.copy(), delta.copy()
    ups[ups < 0] = 0
    downs[downs > 0] = 0

    AU = ups.ewm(com = period-1, min_periods = period).mean()
    AD = downs.abs().ewm(com = period-1, min_periods = period).mean()
    RS = AU/AD

    return pandas.Series(100 - (100/(1 + RS)), name = "RSI")  

# 지정가 매수 함수 (RSI 33넘을 때 값 지정)
def buy(coin):
    # money = upbit.get_balance("KRW")
    ea = float(30000/now_price) #3만원씩 구매
    res = upbit.buy_limit_order(coin, now_price, ea)

# 지정가 전량 매도 함수 (RSI 70일때의 값 지정)
def sell(coin):
    amount = upbit.get_balance(coin)
    cur_price = pyupbit.get_current_price(coin)
    total = amount * cur_price
    res = upbit.sell_limit_order(coin, now_price, amount)

#볼린저밴드 계산
def bollinger_bands(ohlc: pandas.DataFrame, period: int = 20):
    rolling_mean = ohlc['close'].rolling(window=period).mean()
    rolling_std = ohlc['close'].rolling(window=period).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return rolling_mean, upper_band, lower_band

coinlist = ["KRW-BTC", "KRW-XRP", "KRW-ZIL", "KRW-MASK"] 
lower28 = []
higher70 = []

# 초기화
for i in range(len(coinlist)):
    lower28.append(False)
    higher70.append(False)
    
# timecheck = 1
# buycount = 0

#자동 매매 시작
while(True): 
    for i in range(len(coinlist)):
        data = pyupbit.get_ohlcv(ticker=coinlist[i], interval="minute3")
        now_rsi = rsi(data, 14).iloc[-1]
        now_price = data['close'].iloc[-1]
        rolling_mean, upper_band, lower_band = bollinger_bands(data, 20)
        balance2 = upbit.get_avg_buy_price(coinlist[i].split("-")[1]) #각 코인 매수 평균가
 
        if balance2 == None or balance2 == 0 :
            rate_of_return = 0
        else :
            rate_of_return = (now_price - balance2) / (balance2) * 100
        # print(rate_of_return)
        if now_rsi <= 28 and now_price < lower_band[-1] : #장바구니 담기 : RSI 28 미만, 볼린저밴드보다 낮을 때 (보수적인 구매)
            lower28[i] = True

        elif now_rsi >= 33 and lower28[i] == True: #매매 진행
            buy(coinlist[i])
            lower28[i] = False

        elif rate_of_return > 2 and rate_of_return < 50 : #수익률 2% 초과일 때 매도
            sell(coinlist[i])
            higher70[i] = True

        elif rate_of_return < -6 and rate_of_return > -15 : #손실율 6% 초과일 때 손절
            sell(coinlist[i])
            higher70[i] = True
            
        elif now_rsi >= 70 and higher70[i] == False: #rsi 지표만 보고 매도
            sell(coinlist[i])
            higher70[i] = True

        elif now_rsi <= 60 :
            higher70[i] = False
        # print(1)
    now = datetime.datetime.now()
    print(now)
    # if timecheck == 1 or timecheck % 10 == 0 :
    #     print("작동 중입니다.", timecheck)
    # if timecheck == 1 or timecheck % 60 == 0 :
    #     print("Current time is:", now.time())

    # timecheck += 1
    
    time.sleep(1)