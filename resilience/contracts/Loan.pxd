cimport cython
from economicsl.contract cimport Contract

cdef double eps

cdef class Loan(Contract):
    cdef public object parameters
    cdef public double principal
    cdef public double fundingAlreadyPulled
    # must be public because it is overriden by BailinablePullFunding in bail-in paper
    cdef public object _pullfunding
    cdef public object _payloan
    cpdef double get_LCR_weight(self)
    cpdef object get_name(self)
    cpdef void pay_loan(self, long double amount)
    cpdef void reduce_principal(self, long double amount)
    cpdef object get_action(self, object me)
    cpdef bint is_eligible(self, object me)
    cpdef long double get_notional(self)
    cpdef long double get_valuation(self, str side)
    @cython.locals(LGD=double, notional=cython.longdouble)
    cpdef void liquidate(self)
    cpdef void increase_funding_pulled(self, long double fundingPulled)
    cpdef void reduce_funding_pulled(self, long double amount)
    cpdef double get_funding_already_pulled(self)
