"""
Module for optimization models.
"""

import logging

from typing import Optional, Union
from collections import OrderedDict
import re

import numpy as np

from andes.core.common import Config
from andes.core import BaseParam, DataParam, IdxParam, NumParam
from andes.models.group import GroupBase

from ams.core.param import RParam
from ams.core.var import Algeb, RAlgeb

from ams.utils import timer

import cvxpy as cp

logger = logging.getLogger(__name__)


class Var:
    """
    Decision variables in optimization.
    """

    def __init__(self,
                 name: str,
                 lb: Optional[np.ndarray] = - np.inf,
                 ub: Optional[np.ndarray] = np.inf,
                 info: Optional[str] = None,
                 ):
        """
        Decision variables in optimization.

        Parameters
        ----------
        name: str
            Name of the variable.
        type: type, optional
            Type of the variable, by default np.float64
        n: int, optional
            Number of variables, by default 1
        lb: np.ndarray, optional
            Lower bound of the variable, by default - np.inf
        ub: np.ndarray, optional
            Upper bound of the variable, by default np.inf
        info: str, optional
            Information of the variable, by default None
        """
        self.name = name
        self.lb = lb
        self.ub = ub
        self.info = info

        self.type = None  # TODO: var type
        # TODO: add sanity check for lb and ub
        type_ndarray = isinstance(lb, np.ndarray) and isinstance(ub, np.ndarray)
        type_float = isinstance(lb, float) and isinstance(ub, float)

        self.v = None

    @property
    def class_name(self):
        return self.__class__.__name__


class Constraint:
    """
    Base class for constraints.
    """

    def __init__(self,
                 name: Optional[str] = None,
                 e_str: Optional[str] = None,
                 info: Optional[str] = None,
                 type: Optional[str] = 'uq',
                 ):
        self.name = name
        self.e_str = e_str
        self.info = info
        self.type = type  # TODO: determine constraint type

    @property
    def class_name(self):
        return self.__class__.__name__


class Objective:
    """
    Base class for objective functions.
    """

    def __init__(self,
                 e_str: Optional[str] = None,
                 sense: Optional[str] = 'min'):
        self.e_str = e_str
        self.sense = sense


class OModel:
    r"""
    Base class for optimization models.
    The optimziation problem is formulated as:

    .. math::
        \min_x \ & x^_{t} c_{2}^T x + c_{1} x \\
        \mbox{such that} \ & A_{ub} x \leq b_{ub},\\
        & A_{eq} x = b_{eq},\\
        & l \leq x \leq u ,

    where :math:`x` is a vector of decision variables; :math:`c`,
    :math:`b_{ub}`, :math:`b_{eq}`, :math:`l`, and :math:`u` are vectors; and
    :math:`A_{ub}` and :math:`A_{eq}` are matrices.

    # TODO: include integrality parameters.

    The defined arrays and descriptions are as follows:

    +-----------+---------------------------------------------+
    |   Array   |                 Description                 |
    +===========+=============================================+
    |    c2     | quadratic objective coefficients            |
    +-----------+---------------------------------------------+
    |    c1     | linear objective coefficients               |
    +-----------+---------------------------------------------+
    |    Aub    | inequality coefficients                     |
    +-----------+---------------------------------------------+
    |    Aeq    | equality coefficients                       |
    +-----------+---------------------------------------------+
    |    bub    | inequality upper bounds                     |
    +-----------+---------------------------------------------+
    |    beq    | equality bounds                             |
    +-----------+---------------------------------------------+
    |    lb     | decision variable lower bounds              |
    +-----------+---------------------------------------------+
    |    ub     | decision variable upper bounds              |
    +-----------+---------------------------------------------+
    """

    def __init__(self, routine):
        self.routine = routine
        # --- colloect optimziation model ---
        self.mdl = None
        self.vars = OrderedDict()
        self.constrs = OrderedDict()
        self.obj = None
        self.n = 0  # number of decision variables
        self.m = 0  # number of constraints

    @timer
    def setup(self):
        """
        Setup the numerical optimziation formulation from symbolic disaptch model.

        Decision variables are the ``RAlgeb`` of a routine.
        For example, the power outputs ``pg`` of routine ``DCOPF``.

        """
        self.routine.syms.generate_symbols()
        # --- add decision variables ---
        for rname, ralgeb in self.routine.ralgebs.items():
            self.parse_var(ralgeb=ralgeb,
                           sub_map=self.routine.syms.sub_map)
            self.n += ralgeb.n

        # --- parse constraints ---
        for cname, constr in self.routine.constrs.items():
            self.parse_constr(constr=constr,
                              sub_map=self.routine.syms.sub_map)
            self.m += self.constrs[cname].size

        # --- parse objective functions ---
        self.parse_obj(obj=self.routine.obj,
                       sub_map=self.routine.syms.sub_map)

        # --- finalize the optimziation formulation ---
        code_mdl = "problem(self.obj, [constr for constr in self.constrs.values()])"
        for pattern, replacement, in self.routine.syms.sub_map.items():
            code_mdl = re.sub(pattern, replacement, code_mdl)
        code_mdl = "self.mdl=" + code_mdl
        exec(code_mdl)
        return True

    @property
    def class_name(self):
        """
        Return the class name
        """
        return self.__class__.__name__

    def parse_var(self,
                  ralgeb: RAlgeb,
                  sub_map: OrderedDict,
                  ):
        """
        Parse the decision variables from symbolic dispatch model.

        Parameters
        ----------
        var : RAlgeb
            The routine RAlgeb
        sub_map : OrderedDict
            A dictionary of substitution map, generated by symprocessor.
        """
        # only used for CVXPY
        code_var = "tmp=var(ralgeb.n, boolean=(ralgeb.unit == 'bool'))"
        for pattern, replacement, in sub_map.items():
            code_var = re.sub(pattern, replacement, code_var)
        logger.debug(f"var code: {code_var}")
        exec(code_var)
        exec("setattr(self, ralgeb.name, tmp)")
        exec("self.vars[ralgeb.name] = tmp")
        if ralgeb.lb:
            lv = ralgeb.lb.owner.get(src=ralgeb.lb.name, idx=ralgeb.get_idx(), attr='v')
            exec("self.constrs[ralgeb.lb.name] = tmp >= lv")
            self.m += ralgeb.lb.owner.n
        if ralgeb.ub:
            uv = ralgeb.ub.owner.get(src=ralgeb.ub.name, idx=ralgeb.get_idx(), attr='v')
            exec("self.constrs[ralgeb.ub.name] = tmp <= uv")
            self.m += ralgeb.ub.owner.n

    def parse_obj(self,
                  obj: Objective,
                  sub_map: OrderedDict,
                  ):
        """
        Parse the objective function from symbolic dispatch model.

        Parameters
        ----------
        obj : Objective
            The routine Objective
        sub_map : OrderedDict
            A dictionary of substitution map, generated by symprocessor.
        """
        code_obj = obj.e_str
        for pattern, replacement, in sub_map.items():
            code_obj = re.sub(pattern, replacement, code_obj)
        if obj.sense == 'min':
            code_obj = f'cp.Minimize({code_obj})'
        elif obj.sense == 'max':
            code_obj = f'cp.Maximize({code_obj})'
        else:
            raise ValueError(f'Objective sense {obj.sense} is not supported.')
        code_obj = 'self.obj=' + code_obj
        exec(code_obj)
        return True

    def parse_constr(self,
                     constr: Constraint,
                     sub_map: OrderedDict,
                     ):
        """
        Parse the constraint from symbolic dispatch model.
        
        Parameters
        ----------
        constr : Constraint
            The routine Constraint
        sub_map : OrderedDict
            A dictionary of substitution map, generated by symprocessor.
        """
        code_constr = constr.e_str
        for pattern, replacement in sub_map.items():
            code_constr = re.sub(pattern, replacement, code_constr)
        if constr.type == 'uq':
            code_constr = f'{code_constr} <= 0'
        elif constr.type == 'eq':
            code_constr = f'{code_constr} == 0'
        else:
            raise ValueError(f'Objective sense {self.routine.obj.sense} is not supported.')
        code_constr = f'self.constrs["{constr.name}"]=' + code_constr
        exec(code_constr)
