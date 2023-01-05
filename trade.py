#Streaming classes from TDA-API package
from tda.auth import easy_client
from tda.client import Client, base
from tda.streaming import StreamClient

#Indicator classes from TA package
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

#Required Packages
import asyncio
import json
import pandas as pd
from datetime import datetime

#Import files
import config
#Import variables from order.py file
from order import *

'''Login'''
client = easy_client(
        api_key=config.API_KEY,
        redirect_uri=config.REDIRECT_URI,
        token_path=config.TOKEN_PATH)
stream_client = StreamClient(client, account_id=config.ACCOUNT_ID)

#Used to correctly update df_timeframe with time and ticker
cell = 0
not_in_position = True
time_frame = 2
'''Inserts new data into 1min dataframe'''
#Empty 1min dataframe with column headings
df_1min = pd.DataFrame(columns= ['CHART_TIME_UTC','TICKER','OPEN','HIGH','LOW','CLOSE'])
def create_1min_dataframe(data):
    #Creates new pandas dataframe out of new price data
    df_1min_new = pd.read_json(data)
    #Drop unwanted columns
    df_1min_new.drop(columns=['seq', 'VOLUME','SEQUENCE','CHART_DAY'], axis=1, inplace=True)
    #Rename columns
    df_1min_new.rename(columns={'key': 'TICKER','OPEN_PRICE': 'OPEN','HIGH_PRICE': 'HIGH','LOW_PRICE': 'LOW','CLOSE_PRICE':'CLOSE','CHART_TIME':'CHART_TIME_UTC'}, inplace=True)
    #Adds new dataframe to old dataframe
    global df_1min
    df_1min = df_1min.append(df_1min_new, ignore_index=True)

    '''#Keep memory down
    #Delete 1st row of dataframe if length > 480
    if len(df_1min) > 480:
        df_1min = df_1min.drop(index = 0)'''
    return df_1min

'''Covert 1min price data to specified time frame price data'''
#Empty dataframe for desired timeframe
df_timeframe = pd.DataFrame(columns= ['CHART_TIME_UTC','TICKER','OPEN','HIGH','LOW','CLOSE'])
def desired_timeframe_dataframe(df_1min):
    if len(df_1min) >= time_frame:
        #Take means of price data
        df_means = df_1min[["OPEN", "HIGH","LOW","CLOSE"]].mean()
        #Add means of dataframe to specified time frame dataframe
        global df_timeframe
        df_timeframe = df_timeframe.append(df_means, ignore_index=True)
        #Covert Ticker and Time column
        convert_dict = {'TICKER': object}
        df_timeframe = df_timeframe.astype(convert_dict)
        df_timeframe['CHART_TIME_UTC'] = df_timeframe['CHART_TIME_UTC'].apply(pd.to_datetime)
        # Insert time and ticker data
        global cell
        df_timeframe.at[cell, 'CHART_TIME_UTC'] = df_1min.iloc[-1,0]
        df_timeframe.at[cell, 'TICKER'] = df_1min.iloc[-1,1]
        cell+=1
        #Keep memory down
        #Once data is placed in df_timeframe delete it from df_1min
        if len(df_1min) == time_frame:
            for i in range(time_frame):
                df_1min.drop(index = df_1min.index[0], axis=0, inplace=True)
        #return(df_timeframe)
    else:
        print("1 min timeframe \n**Not enough price data yet**")
        print(df_1min)

'''Create indicators,
   add the indicators to end of the pandas dataframe'''
def add_indicators(df):  
    #Add bollinger bands Indicator
    bb_indicator = BollingerBands(df['CLOSE'])
    df['UPPER_BAND'] = bb_indicator.bollinger_hband()
    df['LOWER_BAND']  = bb_indicator.bollinger_lband()
    #Add RSI Indicator
    RSI_Indicator = RSIIndicator(df['CLOSE'])
    df['RSI'] = RSI_Indicator.rsi()
    return(df)

'''Determines when to buy and when to sell'''
def buy_sell_signal(df):
    global not_in_position
    if not_in_position:
        RSI = df.iloc[-1,-1]
        Previous_RSI = df.iloc[-2,-1]
        LOWER_BAND = df.iloc[-1,-2]
        UPPER_BAND = df.iloc[-1,-3]
        CLOSE = df.iloc[-1,-4]
        signal = 'BUY'
        #Long based on oversold signal
        if RSI < 30 and CLOSE < UPPER_BAND:
            #Place Order
            #client.place_order(config.ACCOUNT_ID, payload)
            print("BUYING")
        #Short based on overbought signal
        elif RSI > 70 and df['CLOSE'] > LOWER_BAND :
            print("SHORTING")
        not_in_position = False

'''Replace Order to Maximize Profits'''
def order_builder(df):
    if df['CLOSE'] > df['LOWER_BAND'] :
        MOVING_AVERAGE = (df['LOWER_BAND']+df['UPPER_BAND'])/2
        if df['CLOSE'] > (df['LOWER_BAND']+MOVING_AVERAGE)/2 :
            if df['CLOSE'] > MOVING_AVERAGE :
                if df['CLOSE'] > (MOVING_AVERAGE+df['UPPER_BAND'])/2 :
                    if df['CLOSE'] > df['UPPER_BAND'] :
                        print("Sell")
                    else:
                        print("Set updated_payload = Moving average+Upper / 2. Set trailing_updated_payload = moving average ")
                else:
                    print("Set updated_payload = Moving average. Set trailing_updated_payload = lowerband+moving average /2 ")
            else:
                print("Set updated_payload = lower+moving/2. Set trailing_updated_payload = lowerband")
        else:
            print("Set updated_payload = lower. Set trailing_updated_payload = entered price")



'''Processes the streaming data using a handler'''
def order_book_handler(msg):

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

    #Data is coverted into json string
    #(content data is in a dictionary)'''
    priceData = json.dumps(msg['content'], indent = 4)
    #Function to insert price data into df_1min dataframe
    create_1min_dataframe(priceData)
    #Create desired time frames
    desired_timeframe_dataframe(df_1min)
    #Check to see if desired dataframe is right length for indicators
    if len(df_timeframe) >= 20:
        df_indicators = add_indicators(df_timeframe)
        buy_sell_signal(df_indicators)
    print(str(time_frame)+" min timeframe")
    print(df_timeframe)


'''Streams data and type of data'''
async def read_stream():
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
    await stream_client.chart_equity_subs([symbol])

    stream_client.add_chart_equity_handler(order_book_handler)

    while True:
        await stream_client.handle_message()       

'''Runs Continuously'''
asyncio.get_event_loop().run_until_complete(read_stream())