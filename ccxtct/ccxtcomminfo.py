from cytrader.comminfo import CommInfoBase
import ccxt
from .ccxtstore import CCXTStore


class BinanceCommision(CommInfoBase):
    """
    Simple fixed commission scheme for demo
    """

    params = (
        ("commission", 0.001),
        ("stocklike", True),
        ("commtype", CommInfoBase.COMM_PERC),
        ("percabs", False),
        ("futures", True),
        ("interest", 0.0),
        ("interest_long", False),
        ("store",
            CCXTStore(
                exchange="binance",
                quote="USDT",
                config={},
                retries=5,
            ),
        ),
    )

    def __init__(self):
        super(BinanceCommision, self).__init__()
        if self.p.futures:
            self._creditrate = 0.0001
            self.p.interest_long = True
            self.store = self.p.store

    def _getcommission(self, size, price, pseudoexec):
        if self._commtype == self.COMM_PERC:
            return abs(size) * self.p.commission * price

        return abs(size) * self.p.commission

    def get_last_funding_rate(self, data):
        tkr = data._name
        if data._store:
            response = data._store.exchange.fapiPublicGetPremiumIndex({"symbol": tkr})
        else:
            response = self.store.exchange.fapiPublicGetPremiumIndex({"symbol": tkr})
        return float(response["lastFundingRate"])

    def get_credit_interest(self, data, pos, dt):
        """Roughly calculates the funding fees for Binance futures.
        It assumes that positions accrue interest regardless of
        whether they are open at the funding rate window.
        It also uses the last funding rate, which is inaccurate."""
        if not self.p.futures:
            return 0.0

        size, price = pos.size, pos.price

        if (size == 0) or (size > 0 and not self.p.interest_long):
            return 0.0  # long positions not charged

        dt0 = dt.date()
        dt1 = pos.datetime.date()

        if dt0 <= dt1:
            return 0.0

        if data:
            return self._get_credit_interest(
                data, size, price, (dt0 - dt1).days * 3, dt0, dt1
            )
        else:
            return 0.0

    def _get_credit_interest(self, data, size, price, windows, dt0, dt1):
        self._creditrate = self.get_last_funding_rate(data)
        
        if (size > 0 and self._creditrate > 0.0) or (size < 0.0 and self._creditrate < 0.0):
            return windows * self._creditrate * abs(size) * price
        else:
            return -1 * (windows * self._creditrate * abs(size) * price)
