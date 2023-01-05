'''Contain Specification for order and desired trading time frame'''

#Ticker
symbol = 'F'

#Quantity 
quantity = 1



price = 13
limit = None #Limit order is the lower band. It will then be moved up halfway between moving average and lower.
#Then at moving average, then halfway between moving average and upper. Last moving limit up to order.
#Put oco with trailing stop and limit order togther if above upper band
#Put half of order in current limit and other half in lower limit (in case pullback then continues up)
#Order details
payload = {
  "orderStrategyType": "TRIGGER",
  "session": "NORMAL",
  "duration": "DAY",
  "orderType": "LIMIT",
  "price": price,
  "orderLegCollection": [
    {
      "instruction": "BUY",
      "quantity": quantity,
      "instrument": {
        "assetType": "EQUITY",
        "symbol": symbol
      }
    }
  ],
  "childOrderStrategies": [
    {
      "orderStrategyType": "OCO",
      "childOrderStrategies": [
        {
          "orderStrategyType": "SINGLE",
          "session": "NORMAL",
          "duration": "GOOD_TILL_CANCEL",
          "orderType": "LIMIT",
          "price": price * 1.01,
          "orderLegCollection": [
            {
              "instruction": "SELL",
              "quantity": quantity,
              "instrument": {
                "assetType": "EQUITY",
                "symbol": symbol
              }
            }
          ]
        },
        {
          "orderStrategyType": "SINGLE",
          "session": "NORMAL",
          "duration": "GOOD_TILL_CANCEL",
          "orderType": "STOP",
          "stopPrice": 11.27,
          "orderLegCollection": [
            {
              "instruction": "SELL",
              "quantity": quantity,
              "instrument": {
                "assetType": "EQUITY",
                "symbol": symbol
               }
            }
          ]
        }
      ]
    }
  ]
}
#Updated Profit taking payloads
updatedPayload = {
    "orderType": "STOP",
    "session": "NORMAL",
    "duration": "DAY",
    "stopPrice": 9.0,
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [
      {
        "instruction": "SELL",
        "quantity": quantity/2,
        "instrument": {
          "symbol": symbol,
          "assetType": "EQUITY"
        }
      }
    ]
  }

trailing_updated_payload = {
    "orderType": "STOP",
    "session": "NORMAL",
    "duration": "DAY",
    "stopPrice": 9.0,
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [
      {
        "instruction": "SELL",
        "quantity": quantity/2,
        "instrument": {
          "symbol": symbol,
          "assetType": "EQUITY"
        }
      }
    ]
  }