# ct-ccxt-store
A fork of Dave-Vallance's CCXT Store for compatibility with Cython-based fork of Backtrader, [Cytrader](https://github.com/Saran33/cytrader.git).
- Included a `broker.updatePortfolio` method for setting initial portfolio positions if there are any existing holdings in the account at the time of initial strategy execution.
- Modified `broker.getvalue` to enable rebalancing positions based on a target value.
- Debugged `create_order` to omit a price paramater for market orders, which was throwing errors for Binance futures.
- Debugged `broker.next` method to correctly register (`execute`) both partial and full fills within the Backtrader system, along with their fill value.
- Added support for futures trading, such as `getvalue` returning notional position value if futures mode is activated.
- Added `ccxtcomminfo.py` with a commission info scheme for Binance futures, in order to include a rough calculation for funding rate fees in backtests.
- For a working example, see [_Cytrade](https://github.com/Saran33/_Cytrade).

Installation
============

`pip install git+https://github.com/Saran33/ct-ccxt-store.git`


# Additions / Changes

## CCXTBroker

- Added check for broker fills (complete notification, Cancel notification).
  Note that some exchanges may send different notification data

- Broker mapping added as I noticed that there differences between the expected
  order_types and retuned status's from canceling an order

- Added a new mappings parameter to the script with defaults.

- Added a new get_wallet_balance method. This will allow manual checking of the balance.
  The method will allow setting parameters. Useful for getting margin balances

- Modified getcash() and getvalue():
      Backtrader will call getcash and getvalue before and after next, slowing things down
      with rest calls. As such, these will just return the last values called from getbalance().
      Because getbalance() will not be called by cerebro, you need to do this manually as and when  
      you want the information.

- **Note:** The broker mapping should contain a new dict for order_types and mappings like below:

```
  broker_mapping = {
      'order_types': {
          bt.Order.Market: 'market',
          bt.Order.Limit: 'limit',
          bt.Order.Stop: 'stop-loss', #stop-loss for kraken, stop for bitmex
          bt.Order.StopLimit: 'stop limit'
      },
      'mappings':{
          'closed_order':{
              'key': 'status',
              'value':'closed'
              },
          'canceled_order':{
              'key': 'result',
              'value':1}
              }
      }
```

  - Added new private_end_point method to allow using any private non-unified end point.
    An example for getting a list of postions and then closing them on Bitfinex
    is below:

```
      # NOTE - THIS CLOSES A LONG POSITION. TO CLOSE A SHORT, REMOVE THE '-' FROM
      # -self.position.size
      type = 'Post'
      endpoint = '/positions'
      params = {}
      positions = self.broker.private_end_point(type=type, endpoint=endpoint, params=params)
      for position in positions:
          id = position['id']
          type = 'Post'
          endpoint = '/position/close'
          params = {'position_id': id}
          result = self.broker.private_end_point(type=type, endpoint=endpoint, params=params)
          _pos = self.broker.getposition(data, clone=False)
          # A Price of NONE is returned form the close position endpoint!
          _pos.update(-self.position.size, None)

```

## CCXTStore

Redesigned the way that the store is intialized, data and brokers are requested.
The store now uses metaparams and has methods for `getbroker()` and `getdata()`.
A store is initialized in a similar way to other backtrader stores. e.g

```
# Create a cerebro
  cerebro = bt.Cerebro()

  config = {'urls': {'api': 'https://testnet.bitmex.com'},
                   'apiKey': apikey,
                   'secret': secret,
                   'enableRateLimit': enableRateLimit,
                  }

  # Create data feeds
  store = CCXTStore(exchange='bitmex', currency=currency, config=config, retries=5, debug=False)

  broker = store.getbroker()
  cerebro.setbroker(broker)

  hist_start_date = datetime.utcnow() - timedelta(minutes=fromMinutes)
  data = store.getdata(dataname=symbol, name="LTF",
                           timeframe=get_timeframe(timeframe), fromdate=hist_start_date,
                           compression=1, ohlcv_limit=50, fetch_ohlcv_params = {'partial': False}) #, historical=True)
```

 - Added new private_end_point method to allow using any private non-unified end point. For an example, see broker section above.

## CCXTFeed

- Added option to send some additional fetch_ohlcv_params. Some exchanges (e.g Bitmex) support sending some additional fetch parameters.
- Added drop_newest option to avoid loading incomplete candles where exchanges
  do not support sending ohlcv params to prevent returning partial data
- Added Debug option to enable some additional prints
