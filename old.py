from datetime import datetime, timedelta
weekDay = datetime.now().weekday()
if weekDay == 0 or weekDay == 6:
    quit()
''' ^^^ Get the weekday ^^^ '''
#Market isn't open on weekends, so script won't run

'''Packages'''
#Classes needed to Create Client from TDA-API package
from tda.auth import easy_client
from tda.client import Client

#Indicator classes from TA package
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

#Required Packages
import json
import pandas as pd

#Import files
import config
#Import variables from order.py file
from order import *
#If need to get token: Run get_token.py. 
# Expires every 60 days

'''Create Client'''
client = easy_client(
        api_key=config.API_KEY,
        redirect_uri=config.REDIRECT_URI,
        token_path=config.TOKEN_PATH)

'''Create indicators,
   add the indicators to end of the pandas dataframe'''
def add_indicators(df):  
    #Add bollinger bands Indicator
    bb_indicator = BollingerBands(df['close'])
    df['UPPER_BAND'] = bb_indicator.bollinger_hband()
    df['LOWER_BAND']  = bb_indicator.bollinger_lband()
    #Add RSI Indicator
    RSI_Indicator = RSIIndicator(df['close'])
    df['RSI'] = RSI_Indicator.rsi()
    return(df)

'''Determines when to buy and when to sell'''
def buy_sell_signal(df,RSI, LOWER_BAND, UPPER_BAND, CLOSE, not_in_position):
    if not_in_position is True:
        #Long based on oversold signal
        if RSI < 30 and CLOSE < LOWER_BAND:
            #Place Order
            #client.place_order(config.ACCOUNT_ID, payload)
            print("BUYING")
            signal = True
            return signal
            
        #Short based on overbought signal
        elif RSI > 70 and CLOSE > UPPER_BAND :
            print("SHORTING")

'''Replace Order to Maximize Profits'''
def order_builder(df,RSI, lower_band, upper_band, close):
    if close > lower_band :
        moving_average = (lower_band+upper_band)/2
        if close > (lower_band+moving_average)/2 :
            if close > moving_average :
                if close > (moving_average+upper_band)/2 :
                    if close > upper_band:
                        print("Sell")
                    else:
                        print("Set updated_payload = Moving average+Upper / 2. Set trailing_updated_payload = moving average ")
                else:
                    print("Set updated_payload = Moving average. Set trailing_updated_payload = lowerband+moving average /2 ")
            else:
                print("Set updated_payload = lower+moving/2. Set trailing_updated_payload = lowerband")
        else:
            print("Set updated_payload = lower. Set trailing_updated_payload = entered price")

        '''Get and Replace Previous order'''
    '''#Get previous order out of json
    previousOrderId = client.get_orders_by_path(config.ACCOUNT_ID,max_results=1, from_entered_datetime=datetime(2021,8,10), to_entered_datetime=datetime(2021,8,10))
    previousOrderId = previousOrderId.json()
    previousOrderId = previousOrderId[0]['childOrderStrategies'][0]['orderId']
    #Get previous order using orderId from json
    previousOrder = client.get_order(order_id = previousOrderId,account_id= config.ACCOUNT_ID).json()
    #print(json.dumps(previousOrder, indent = 4))
    #Replace order
    replaced = client.replace_order(config.ACCOUNT_ID, previousOrder, payload)
    #print(replaced)'''

'''Get todays date'''
#(needed to pull price data)
day = datetime.now().day
month = datetime.now().month
year = datetime.now().year
today = datetime(year,month,day)
next_friday = today + timedelta((4-today.weekday()) % 7 )


'''Get 15 min candles'''
#Gets 15 min candles for the day for specificed symbol

'''candles = client.get_price_history(symbol,
        frequency=Client.PriceHistory.Frequency.EVERY_FIFTEEN_MINUTES,
        start_datetime=datetime(year,month,day-1),
        end_datetime = datetime(year,month,day),
        need_extended_hours_data = False).json()

candles = (json.dumps(candles['candles']))

df = pd.read_json(candles)
df.drop(['open','high','low','volume'], axis=1, inplace=True)'''


'''Get Option Chain'''
#Get option chain and options ids to build vertical spread
#If <Response [200 OK]> add .json() to end

option_chain = client.get_option_chain(symbol,
        contract_type = client.Options.ContractType.PUT,
        strike_count = 2,
        from_date= today,
        to_date=next_friday).json()
option_chain = json.dumps(option_chain['putExpDateMap'], indent= 4)
option_chain = json.loads(option_chain)
option_chain = option_chain[list(option_chain)[0]]

#Get short option id
short_id = option_chain[list(option_chain)[0]][0]['symbol']

#Get long option id
long_id = option_chain[list(option_chain)[1]][0]['symbol']



print(short_id)
#F_122321P19.5
print(long_id)
'''
#Position variable
not_in_position = True
df = add_indicators(df)
RSI = df.iloc[-1,-1]
Previous_RSI = df.iloc[-2,-1]
LOWER_BAND = df.iloc[-1,-2]
UPPER_BAND = df.iloc[-1,-3]
CLOSE = df.iloc[-1,0]
signal = buy_sell_signal(df, RSI, LOWER_BAND, UPPER_BAND, CLOSE, not_in_position)
if signal is True:
        order_builder(df,RSI, LOWER_BAND, UPPER_BAND, CLOSE)
        not_in_position = False'''


'''if not_in_position is False:
        print("In long position")'''