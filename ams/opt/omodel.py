"""
Module for optimization models.
"""

import logging

from typing import Optional, Union
from collections import OrderedDict

import numpy as np

from andes.core.common import Config
from andes.core import NumParam

from ams.core.var import RAlgeb
from ams.opt.ovar import OVar
from ams.opt.constraint import Constraint
from ams.opt.objective import Objective

logger = logging.getLogger(__name__)


class OModel:
    """
    Base class for optimization models.
    """

    def __init__(self):
        self.vars = OrderedDict()
        self.constraints = OrderedDict()
        self.objective = None

    def init(self):
        pass

    def add_Rvars(self,
                  RAlgeb: Union[RAlgeb, str],
                  lb: Optional[Union[NumParam, str]] = None,
                  ub: Optional[Union[NumParam, str]] = None,
                  ):
        """
        Add RAlgeb as variables.
        """
        name = RAlgeb.name
        type = RAlgeb.type
        n = RAlgeb.owner.n
        lb = - np.inf if lb is None else lb.v
        ub = np.inf if ub is None else ub.v
        var = OVar(name=name, type=type, n=n, lb=lb, ub=ub)
        self.vars[name] = var
        return var

    def add_vars(self,
                 name='var',
                 type: Optional[type] = np.float64,
                 n: Optional[int] = 1,
                 lb: Optional[np.ndarray] = - np.inf,
                 ub: Optional[np.ndarray] = np.inf,
                 ):
        var = OVar(name=name, type=type, n=n, lb=lb, ub=ub)
        self.vars[name] = var
        setattr(self, name, var)
        return var

    def add_constraints(self, *args, **kwargs):
        self.constraints.add(*args, **kwargs)

    def add_objective(self, *args, **kwargs):
        self.objectives.add(*args, **kwargs)