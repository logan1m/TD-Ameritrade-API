from datetime import datetime, timedelta
'''weekDay = datetime.now().weekday()
if weekDay == 5 or weekDay == 6:
    quit()'''
''' ^^^ Get the weekday ^^^ '''
#Market isn't open on weekends, so script won't run

'''Packages'''
#Classes needed to Create Client from TDA-API package
from tda.auth import easy_client
from tda.client import Client

#Required Packages
import json
import pandas as pd

#Import files
import config
#Import variables from order.py file
symbol = 'F'
quantity = 1

#If need to get token: Run get_token.py. 
# Expires every 60 days

'''Create Client'''
client = easy_client(
        api_key=config.API_KEY,
        redirect_uri=config.REDIRECT_URI,
        token_path=config.TOKEN_PATH)

'''Get required dates'''
#(needed to pull price data)
today = datetime.now()
nextFriday = today + timedelta((4-today.weekday()) % 7 )

'''Determine if already in position'''
in_Vertical = False
#Get previous order
'''previousOrder = client.get_orders_by_path(config.ACCOUNT_ID,max_results=1, from_entered_datetime=datetime(today.year,today.month,today.day-1), to_entered_datetime=today)
previousOrder = previousOrder.json()

#If the previous order is not empty update to in position
if previousOrder != [] :
        previousOrderId = previousOrder[0]['orderId']
        if previousOrder[0]['complexOrderStrategyType'] == 'VERTICAL':
                in_Vertical = True
                print('open position')
'''
'''Get Option Chain'''
#Get option chain
optionChain = client.get_option_chain(symbol,
        contract_type = client.Options.ContractType.PUT,
        strike_count = 2,
        from_date= today,
        to_date=nextFriday).json()
optionChain = json.dumps(optionChain['putExpDateMap'])
optionChain = json.loads(optionChain)
optionChain = optionChain[list(optionChain)[0]]
'''Place and Adjust Initial Vertical Spread'''
'''
#If <Response [200 OK]> add .json() to end
#Get option chain and options ids to build vertical spread
if in_Vertical is False:
        #Get long option id
        longId = optionChain[list(optionChain)[0]][0]['symbol']
        #Get short option id
        shortId = optionChain[list(optionChain)[1]][0]['symbol']

        #Order to open initial short put vertical position
        #Order Specs
        orderSpecs = {
        "session": "NORMAL",
        "duration": "DAY",
        "orderType": "NET_CREDIT",
        "orderStrategyType": "SINGLE",
        "complexOrderStrategyType": "VERTICAL",
        "price": 0.0637,
        "orderLegCollection": [
        {
        "orderLegType": "OPTION",
        "instrument": {
                "symbol": shortId,
                "assetType": "OPTION"
        },
        "instruction": "SELL_TO_OPEN",
        "quantity": quantity
        },
        {
        "orderLegType": "OPTION",
        "instrument": {
                "symbol": longId,
                "assetType": "OPTION"
        },
        "instruction": "BUY_TO_OPEN",
        "quantity": quantity
        }
        ]
        }
        #Place Order
        client.place_order(config.ACCOUNT_ID, orderSpecs)
        print('order submitted')
#Adjust Order by Sell long put
else:
        #Sell to close long put
        #Get previous order using orderId from json
        previousOrder = client.get_order(order_id = previousOrderId,account_id= config.ACCOUNT_ID).json()
        #Get symbol id for long put
        longId = json.dumps(previousOrder['orderLegCollection'][1]['instrument']['symbol'])

        #Updated Order Specs
        updatedOrderSpec = {
        "orderType": "MARKET",
        "session": "NORMAL",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
        {
        "instrument": {
                "assetType": "OPTION",
                "symbol": longId
        },
        "instruction": "SELL_TO_CLOSE",
        "quantity": quantity
        }
        ]
        }
        client.cancel_order(order_id = previousOrderId, account_id = config.ACCOUNT_ID)
        print('order canceled')
        #client.replace_order(account_id = config.ACCOUNT_ID, order_id = previousOrderId, order_spec = updatedOrderSpec)
        #print('order updated')
'''

'''After Short Put Assigned'''
#If rejected: will say already in position
#Already be in itm long put
optionChain = client.get_option_chain(symbol,
        contract_type = client.Options.ContractType.PUT,
        strike_count = 4,
        from_date= today,
        to_date=nextFriday).json()
optionChain = json.dumps(optionChain['putExpDateMap'])
optionChain = json.loads(optionChain)
optionChain = optionChain[list(optionChain)[0]]
#Get long itm put option id
longitmPutId = optionChain[list(optionChain)[3]][0]['symbol']
verticalLongPutId = optionChain[list(optionChain)[0]][0]['symbol']
verticalShortPutId = optionChain[list(optionChain)[1]][0]['symbol']
print(longitmPutId)
print(verticalLongPutId)
print(verticalShortPutId)
'''
protectivePutOrderSpec = {
  "session": "NORMAL",
  "duration": "DAY",
  "orderStrategyType": "SINGLE",
  "orderType": "LIMIT",
  "price": 12.0,
  "orderLegCollection": [
    {
      "instruction": "BUY_TO_OPEN",
      "quantity": quantity,
      "instrument": {
        "assetType": "OPTION",
        "symbol": "longId"
      }
    }
  ]
}
#Place Order
client.place_order(config.ACCOUNT_ID, protectivePutOrderSpecs)
print('order submitted')'''
#Sell Credit Spread at same time of itm put
#Order to open initial short put vertical position
#Order Specs
'''
verticalOrderSpecs = {
  "session": "NORMAL",
  "duration": "DAY",
  "orderType": "NET_CREDIT",
  "orderStrategyType": "SINGLE",
  "complexOrderStrategyType": "VERTICAL",
  "price": 100,
  "orderLegCollection": [
    {
      "orderLegType": "OPTION",
      "instrument": {
        "symbol": verticalShortPutId,
        "assetType": "OPTION"
      },
      "instruction": "SELL_TO_OPEN",
      "quantity": quantity
    },
    {
      "orderLegType": "OPTION",
      "instrument": {
        "symbol": verticalLongPutId,
        "assetType": "OPTION"
      },
      "instruction": "BUY_TO_OPEN",
      "quantity": quantity
    }
  ]
}
#Place Order
client.place_order(config.ACCOUNT_ID, verticalOrderSpecs)
print('order submitted')'''
#Get call option info
#Sell call ratio after short put assigned
'''callRatioOrderSpec = {
  "orderType": "NET_CREDIT",
  "session": "NORMAL",
  "price": 4.13,
  "duration": "DAY",
  "orderStrategyType": "SINGLE",
  "orderLegCollection": [
    {
      "instruction": "BUY_TO_OPEN",
      "quantity": quantity,
      "instrument": {
        "symbol": "XYZ_011516C45",
        "assetType": "OPTION"
      }
    },
    {
      "instruction": "SELL_TO_OPEN",
      "quantity": quantity *2,
      "instrument": {
        "symbol": "XYZ_011516C42",
        "assetType": "OPTION"
      }
    }
  ]
}
client.place_order(config.ACCOUNT_ID, callRatioOrderSpecs)
print('order submitted')'''

'''Close short call ratio/ long put'''

'''Automatically Find earnings/high iv stocks'''