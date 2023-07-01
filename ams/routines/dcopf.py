"""
OPF routines.
"""
from collections import OrderedDict
import numpy as np
from scipy.optimize import linprog

from ams.core.param import RParam

from ams.routines.routine import RoutineData, RoutineModel

from ams.opt.omodel import Var, Constraint, Objective


class DCOPFData(RoutineData):
    """
    DCOPF data.
    """

    def __init__(self):
        RoutineData.__init__(self)
        # --- generator cost ---
        self.c2 = RParam(info='Gen cost coefficient 2',
                         name='c2',
                         tex_name=r'c_{2}',
                         unit=r'$/(p.u.^2)',
                         owner_name='GCost',
                         )
        self.c1 = RParam(info='Gen cost coefficient 1',
                         name='c1',
                         tex_name=r'c_{1}',
                         unit=r'$/(p.u.)',
                         owner_name='GCost',
                         )
        self.c0 = RParam(info='Gen cost coefficient 0',
                         name='c0',
                         tex_name=r'c_{0}',
                         unit=r'$',
                         owner_name='GCost',
                         )
        # --- generator limit ---
        self.pmax = RParam(info='generator maximum active power (system base)',
                           name='pmax',
                           tex_name=r'p_{max}',
                           unit='p.u.',
                           owner_name='StaticGen',
                           )
        self.pmin = RParam(info='generator minimum active power (system base)',
                           name='pmin',
                           tex_name=r'p_{min}',
                           unit='p.u.',
                           owner_name='StaticGen',
                           )
        # --- load ---
        # NOTE: following two parameters are temporary solution
        self.pd1 = RParam(info='active power load on gen bus',
                          name='pd1',
                          tex_name=r'p_{d1}',
                          unit='p.u.',
                          )
        self.pd2 = RParam(info='active power load on non-gen bus',
                          name='pd2',
                          tex_name=r'p_{d2}',
                          unit='p.u.',
                          )
        # --- line ---
        self.rate_a = RParam(info='long-term flow limit flow limit',
                             name='rate_a',
                             tex_name=r'R_{ATEA}',
                             unit='MVA',
                             owner_name='Line',
                             )
        self.PTDF1 = RParam(info='PTDF matrix for gen bus',
                            name='PTDF1',
                            tex_name=r'P_{TDF1}',
                            )
        self.PTDF2 = RParam(info='PTDF matrix for non-gen bus',
                            name='PTDF2',
                            tex_name=r'P_{TDF2}',
                            )


class DCOPFBase(RoutineModel):
    """
    Base class for DCOPF dispatch model.

    Overload the ``solve``, ``unpack``, and ``run`` methods.
    """

    def __init__(self, system, config):
        RoutineModel.__init__(self, system, config)

    def solve(self, **kwargs):
        """
        Solve the routine optimization model.
        """
        res = self.om.mdl.solve(**kwargs)
        return res

    def run(self, **kwargs):
        """
        Run the routine.

        Other Parameters
        ----------------
        solver: str, optional
            The solver to use. For example, 'GUROBI', 'ECOS', 'SCS', or 'OSQP'.
        verbose : bool, optional
            Overrides the default of hiding solver output and prints logging information describing CVXPY's compilation process.
        gp : bool, optional
            If True, parses the problem as a disciplined geometric program instead of a disciplined convex program.
        qcp : bool, optional
            If True, parses the problem as a disciplined quasiconvex program instead of a disciplined convex program.
        requires_grad : bool, optional
            Makes it possible to compute gradients of a solution with respect to Parameters by calling problem.backward()
            after solving, or to compute perturbations to the variables given perturbations to Parameters by calling problem.derivative().
            Gradients are only supported for DCP and DGP problems, not quasiconvex problems. When computing gradients
            (i.e., when this argument is True), the problem must satisfy the DPP rules.
        enforce_dpp : bool, optional
            When True, a DPPError will be thrown when trying to solve a non-DPP problem (instead of just a warning).
            Only relevant for problems involving Parameters. Defaults to False.
        ignore_dpp : bool, optional
            When True, DPP problems will be treated as non-DPP, which may speed up compilation. Defaults to False.
        method : function, optional
            A custom solve method to use.
        kwargs : keywords, optional
            Additional solver specific arguments. See CVXPY documentation for details.
        """
        return RoutineModel.run(self, **kwargs)

    def unpack(self, **kwargs):
        """
        Unpack the results from CVXPY model.
        """
        # --- copy results from solver into routine algeb ---
        for raname, var in self.vars.items():
            ovar = getattr(self.om, raname)
            var.v = getattr(ovar, 'value')
            # --- copy results from routine algeb into system algeb ---
            if var.owner_name is None:          # if no owner
                continue
            else:
                owner = getattr(self.system, var.owner_name)
                try:
                    idx = owner.get_idx()
                except AttributeError:
                    idx = owner.idx.v
                else:
                    continue
                owner.set(src=var.src, attr='v', idx=idx, value=var.v)
        self.obj.v = self.om.obj.value
        self.system.recent = self.system.routines[self.class_name]
        return True


class DCOPFModel(DCOPFBase):
    """
    DCOPF model.
    """

    def __init__(self, system, config):
        DCOPFBase.__init__(self, system, config)
        self.info = 'DC Optimal Power Flow'
        self.type = 'DCED'
        # --- vars ---
        self.pg = Var(info='active power generation (system base)',
                      unit='p.u.',
                      name='pg',
                      src='p',
                      tex_name=r'p_{g}',
                      owner_name='StaticGen',
                      lb=self.pmin,
                      ub=self.pmax,
                      )
        # --- constraints ---
        self.pb = Constraint(name='pb',
                             info='power balance',
                             e_str='sum(pd1) + sum(pd2) - sum(pg)',
                             type='eq',
                             )
        self.lub = Constraint(name='lub',
                              info='line limits upper bound',
                              e_str='PTDF1 @ (pg - pd1) - PTDF2 * pd2 - rate_a',
                              type='uq',
                              )
        self.llb = Constraint(name='llb',
                              info='line limits lower bound',
                              e_str='- PTDF1 @ (pg - pd1) + PTDF2 * pd2 - rate_a',
                              type='uq',
                              )
        # --- objective ---
        self.obj = Objective(name='tc',
                             info='total cost',
                             e_str='sum(c2 * pg**2 + c1 * pg + c0)',
                             sense='min',)


class DCOPF(DCOPFData, DCOPFModel):
    """
    Standard DC optimal power flow (DCOPF).

    In this model, the power demand ``pd`` is reorganized as ``pd1`` and ``pd2``,
    where ``pd1`` is the load connected to generator bus and ``pd2`` is the load
    connected to non-generator bus.

    Similarly, power transfer distribution factor (PTDF) matrix ``PTDF`` is reorganized
    as ``PTDF1`` and ``PTDF2``, where ``PTDF1`` is the matrix for generator bus
    and ``PTDF2`` is the matrix for non-generator bus.
    """

    def __init__(self, system, config):
        DCOPFData.__init__(self)
        DCOPFModel.__init__(self, system, config)
