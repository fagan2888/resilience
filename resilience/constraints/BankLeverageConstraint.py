import logging

import numpy as np

from ..parameters import eps


class BankLeverageConstraint(object):
    r"""
    1 > \lambda_{buffer} (BANK_LEVERAGE_BUFFER) > \lambda_{min} (BANK_LEVERAGE_MIN)
    """
    __slots__ = 'me',

    def __init__(self, me) -> None:
        self.me = me

    def get_leverage_buffer(self) -> np.longdouble:
        if hasattr(self.me, 'leverage_buffer'):
            return self.me.leverage_buffer
        return self.me.model.parameters.BANK_LEVERAGE_BUFFER

    def is_insolvent(self, cached_equity=None) -> bool:
        lev = self.me.get_leverage(cached_equity)
        insolvent = lev < (self.me.model.parameters.BANK_LEVERAGE_MIN - eps)
        if insolvent:
            logging.debug(f"My leverage is {lev} which is below the minimum")
        return insolvent

    def get_leverage_target(self) -> np.longdouble:
        if hasattr(self.me, 'leverage_target'):
            return self.me.leverage_target
        return self.me.model.parameters.BANK_LEVERAGE_TARGET

    def get_amount_to_delever(self) -> np.longdouble:
        r"""
        Deleverage just enough to reach \lambda_{target}
        Ref: Cont and Schaanning 2017
        """
        lev = self.me.get_leverage()
        is_below_buffer = lev < (self.get_leverage_buffer() - eps)
        if not is_below_buffer:
            # leverage ratio is still at safe zone
            return 0.0
        CET1E = self.me.get_CET1E()
        current = CET1E / lev
        target = CET1E / self.get_leverage_target()
        return max(0, current - target)

    def get_leverage_denominator(self, cached_asset=None):
        if cached_asset is None:
            return self.me.get_ledger().get_asset_value() - self.me.DeltaA
        return cached_asset - self.me.DeltaA
