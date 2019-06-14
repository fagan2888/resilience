cimport cython
from economicsl.contract cimport Contract

cdef class Loan(Contract):
    cdef public object parameters
    cdef public double principal
    cdef public double fundingAlreadyPulled
    cdef object _pullfunding
    cdef object _payloan
    cpdef double get_LCR_weight(self)
    cpdef object get_name(self)
    cpdef void pay_loan(self, long double amount)
    cpdef void reduce_principal(self, long double amount)
    cpdef void reduce_pull_funding_amount(self, long double amount)
    cpdef object get_action(self, object me)
    cpdef bint is_eligible(self, object me)
    cpdef double get_notional(self)
    cpdef long double get_valuation(self, str side)
    cpdef void liquidate(self)
    cpdef void increase_funding_pulled(self, long double fundingPulled)
    cpdef double get_funding_already_pulled(self)
