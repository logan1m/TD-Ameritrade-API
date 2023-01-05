'''Contain Specification for order and desired trading time frame'''
from test import short_id, long_id
symbol = 'F'
quantity = 1

payload = {
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
        "symbol": short_id,
        "assetType": "OPTION"
      },
      "instruction": "SELL_TO_OPEN",
      "quantity": quantity
    },
    {
      "orderLegType": "OPTION",
      "instrument": {
        "symbol": long_id,
        "assetType": "OPTION"
      },
      "instruction": "BUY_TO_OPEN",
      "quantity": quantity
    }
  ]
}