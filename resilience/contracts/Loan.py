import logging

from ..actions import PayLoan, PullFunding
from economicsl import Contract
from ..parameters import eps


class Loan(Contract):
    __slots__ = 'principal', 'fundingAlreadyPulled', 'parameters', '_pullfunding', '_payloan'
    ctype = 'Loan'

    def __init__(self, assetParty, liabilityParty, principal):
        super().__init__(assetParty, liabilityParty)
        _model = (assetParty or liabilityParty).model
        self.parameters = _model.parameters
        self.principal = principal
        self.fundingAlreadyPulled = 0
        # PERF for caching purpose
        self._pullfunding = PullFunding(assetParty, self)
        self._payloan = PayLoan(liabilityParty, self)

    def get_LCR_weight(self):
        return self.parameters.INTERBANK_LCR

    def get_name(self, me):
        if me == self.assetParty:
            if self.liabilityParty is None:
                return "Loan to external node"
            return "Loan to " + self.liabilityParty.get_name()
        else:
            if self.assetParty is None:
                return "Loan from external node"
            return "Loan from " + self.assetParty.get_name()

    def pay_loan(self, amount):
        # update the amount required to be paid because it could have decreased due to bail-in
        amount = min(amount, self.get_value())

        if self.liabilityParty is not None:
            self.liabilityParty.pay_liability(amount, self)
            self.liabilityParty.get_ledger().subtract_cash(amount)
            #if self.assetParty is not None:
            #    # TODO fix accounting where assetParty does pull_funding
            #    self.liabilityParty.send_cash(self.assetParty, amount)
        if self.assetParty is not None:
        #elif self.assetParty is not None:
            # the case when external node pays back to asset party, which
            # happens instantaneously
            self.assetParty.get_ledger().pull_funding(amount, self)
            self.assetParty.get_ledger().add_cash(amount)
        self.reduce_principal(amount)

    def reduce_principal(self, amount):
        value = self.get_value()
        assert (value - amount) >= -eps, (value, amount)
        self.principal -= amount
        self.principal = abs(self.principal)  # round off floating error

        if self.principal < 0.01:
            logging.debug("This loan between " + (self.assetParty.get_name() if self.assetParty else 'None') + ' and ' + (self.liabilityParty.get_name() if self.liabilityParty else 'None') + " has been fully repaid.")
            # TODO: Destroy the loan

    def reduce_pull_funding_amount(self, amount):
        self.fundingAlreadyPulled -= amount

    def get_action(self, me):
        if self.assetParty == me:
            return self._pullfunding
        elif self.liabilityParty == me:
            return self._payloan

    def is_eligible(self, me):
        value = self.get_value()
        return (value > 0) and (value > self.get_funding_already_pulled())
        # TODO: include assetParty.is_alive() and liabilityParty.isAlive()

    def get_value(self):
        return self.principal

    def liquidate(self):
        if self.assetParty is None:
            return
        if self.parameters.ENDOGENOUS_LGD_ON:
            LGD = self.liabilityParty.endogenous_LGD
        else:
            if hasattr(self.liabilityParty, 'exogenous_LGD'):
                LGD = self.liabilityParty.exogenous_LGD
            else:
                LGD = self.parameters.INTERBANK_LOSS_GIVEN_DEFAULT
        value = self.get_value()
        self.assetParty.get_ledger().devalue_asset(self, value)
        self.assetParty.add_cash(value * (1.0 - LGD))
        # TODO uncomment this for correct accounting
        # self.liabilityParty.get_ledger().devalue_liability(self, value)
        self.fundingAlreadyPulled = 0
        self.principal = 0.0

    def increase_funding_pulled(self, fundingPulled):
        self.fundingAlreadyPulled += fundingPulled

    def get_funding_already_pulled(self):
        return self.fundingAlreadyPulled
