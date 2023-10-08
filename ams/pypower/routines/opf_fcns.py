"""
Modules for OPF additional functions.
"""

# --- hessfcn ---

from numpy import array, zeros, ones, exp, arange, r_, flatnonzero as find
from scipy.sparse import vstack, hstack, issparse, csr_matrix as sparse


from ams.pypower.polycost import polycost

from ams.pypower.make import (d2Sbus_dV2, dSbus_dV, dIbr_dV,
                              d2AIbr_dV2, d2ASbr_dV2, dSbr_dV)
from ams.pypower.opf_costfcn import opf_costfcn
from ams.pypower.opf_consfcn import opf_consfcn

# --- consfcn ---
from numpy import zeros, ones, conj, exp, r_, Inf, arange

from scipy.sparse import lil_matrix, vstack, hstack, csr_matrix as sparse


from ams.pypower.make import (makeSbus, dSbus_dV, dIbr_dV,
                              dSbr_dV, dAbr_dV)

# --- costfcn ---
from numpy import array, ones, zeros, arange, r_, dot, flatnonzero as find
from scipy.sparse import issparse, csr_matrix as sparse


from ams.pypower.totcost import totcost
from ams.pypower.polycost import polycost

# --- run_userfcn ---
from ams.pypower.util import feval


from ams.pypower.idx_gen import PG, QG
from ams.pypower.idx_brch import F_BUS, T_BUS
from ams.pypower.idx_cost import MODEL, POLYNOMIAL
from ams.pypower.idx_cost import MODEL, POLYNOMIAL
from ams.pypower.idx_gen import GEN_BUS, PG, QG
from ams.pypower.idx_brch import F_BUS, T_BUS, RATE_A


def opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt, il=None, cost_mult=1.0):
    """Evaluates Hessian of Lagrangian for AC OPF.

    Hessian evaluation function for AC optimal power flow, suitable
    for use with L{pips}.

    Examples::
        Lxx = opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt)
        Lxx = opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt, il)
        Lxx = opf_hessfcn(x, lmbda, om, Ybus, Yf, Yt, ppopt, il, cost_mult)

    @param x: optimization vector
    @param lmbda: C{eqnonlin} - Lagrange multipliers on power balance
    equations. C{ineqnonlin} - Kuhn-Tucker multipliers on constrained
    branch flows.
    @param om: OPF model object
    @param Ybus: bus admittance matrix
    @param Yf: admittance matrix for "from" end of constrained branches
    @param Yt: admittance matrix for "to" end of constrained branches
    @param ppopt: PYPOWER options vector
    @param il: (optional) vector of branch indices corresponding to
    branches with flow limits (all others are assumed to be unconstrained).
    The default is C{range(nl)} (all branches). C{Yf} and C{Yt} contain
    only the rows corresponding to C{il}.
    @param cost_mult: (optional) Scale factor to be applied to the cost
    (default = 1).

    @return: Hessian of the Lagrangian.

    @see: L{opf_costfcn}, L{opf_consfcn}

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    """
    # ----- initialize -----
    # unpack data
    ppc = om.get_ppc()
    baseMVA, bus, gen, branch, gencost = \
        ppc["baseMVA"], ppc["bus"], ppc["gen"], ppc["branch"], ppc["gencost"]
    cp = om.get_cost_params()
    N, Cw, H, dd, rh, kk, mm = \
        cp["N"], cp["Cw"], cp["H"], cp["dd"], cp["rh"], cp["kk"], cp["mm"]
    vv, _, _, _ = om.get_idx()

    # unpack needed parameters
    nb = bus.shape[0]  # number of buses
    nl = branch.shape[0]  # number of branches
    ng = gen.shape[0]  # number of dispatchable injections
    nxyz = len(x)  # total number of control vars of all types

    # set default constrained lines
    if il is None:
        il = np.arange(nl)  # all lines have limits by default
    nl2 = len(il)  # number of constrained lines

    # grab Pg & Qg
    Pg = x[vv["i1"]["Pg"]:vv["iN"]["Pg"]]  # active generation in p.u.
    Qg = x[vv["i1"]["Qg"]:vv["iN"]["Qg"]]  # reactive generation in p.u.

    # put Pg & Qg back in gen
    gen[:, IDX.gen.PG] = Pg * baseMVA  # active generation in MW
    gen[:, IDX.gen.QG] = Qg * baseMVA  # reactive generation in MVAr

    # reconstruct V
    Va = x[vv["i1"]["Va"]:vv["iN"]["Va"]]
    Vm = x[vv["i1"]["Vm"]:vv["iN"]["Vm"]]
    V = Vm * np.exp(1j * Va)
    nxtra = nxyz - 2 * nb
    pcost = gencost[np.arange(ng), :]
    if gencost.shape[0] > ng:
        qcost = gencost[np.arange(ng, 2 * ng), :]
    else:
        qcost = np.array([])

    # ----- evaluate d2f -----
    d2f_dPg2 = np.zeros(ng)  # c_sparse((ng, 1))               ## w.r.t. p.u. Pg
    d2f_dQg2 = np.zeros(ng)  # c_sparse((ng, 1))               ## w.r.t. p.u. Qg
    ipolp = find(pcost[:, IDX.cost.MODEL] == IDX.cost.POLYNOMIAL)
    d2f_dPg2[ipolp] = \
        baseMVA**2 * polycost(pcost[ipolp, :], Pg[ipolp] * baseMVA, 2)
    if np.any(qcost):  # Qg is not free
        ipolq = find(qcost[:, IDX.cost.MODEL] == IDX.cost.POLYNOMIAL)
        d2f_dQg2[ipolq] = \
            baseMVA**2 * polycost(qcost[ipolq, :], Qg[ipolq] * baseMVA, 2)
    i = np.r_[np.arange(vv["i1"]["Pg"], vv["iN"]["Pg"]),
              np.arange(vv["i1"]["Qg"], vv["iN"]["Qg"])]
#    d2f = c_sparse((vstack([d2f_dPg2, d2f_dQg2]).toarray().flatten(),
#                  (i, i)), shape=(nxyz, nxyz))
    d2f = c_sparse((np.r_[d2f_dPg2, d2f_dQg2], (i, i)), (nxyz, nxyz))

    # generalized cost
    if issparse(N) and N.nnz > 0:
        nw = N.shape[0]
        r = N * x - rh  # Nx - rhat
        iLT = find(r < -kk)  # below dead zone
        iEQ = find((r == 0) & (kk == 0))  # dead zone doesn't exist
        iGT = find(r > kk)  # above dead zone
        iND = np.r_[iLT, iEQ, iGT]  # rows that are Not in the Dead region
        iL = find(dd == 1)  # rows using linear function
        iQ = find(dd == 2)  # rows using quadratic function
        LL = c_sparse((np.ones(len(iL)), (iL, iL)), (nw, nw))
        QQ = c_sparse((np.ones(len(iQ)), (iQ, iQ)), (nw, nw))
        kbar = c_sparse((np.r_[np.ones(len(iLT)), np.zeros(len(iEQ)), -np.ones(len(iGT))],
                         (iND, iND)), (nw, nw)) * kk
        rr = r + kbar  # apply non-dead zone shift
        M = c_sparse((mm[iND], (iND, iND)), (nw, nw))  # dead zone or scale
        diagrr = c_sparse((rr, (np.arange(nw), np.arange(nw))), (nw, nw))

        # linear rows multiplied by rr(i), quadratic rows by rr(i)^2
        w = M * (LL + QQ * diagrr) * rr
        HwC = H * w + Cw
        AA = N.T * M * (LL + 2 * QQ * diagrr)

        d2f = d2f + AA * H * AA.T + 2 * N.T * M * QQ * \
            c_sparse((HwC, (np.arange(nw), np.arange(nw))), (nw, nw)) * N
    d2f = d2f * cost_mult

    # ----- evaluate Hessian of power balance constraints -----
    nlam = int(len(lmbda["eqnonlin"]) / 2)
    lamP = lmbda["eqnonlin"][:nlam]
    lamQ = lmbda["eqnonlin"][nlam:nlam + nlam]
    Gpaa, Gpav, Gpva, Gpvv = d2Sbus_dV2(Ybus, V, lamP)
    Gqaa, Gqav, Gqva, Gqvv = d2Sbus_dV2(Ybus, V, lamQ)

    d2G = vstack([
        hstack([
            vstack([hstack([Gpaa, Gpav]),
                    hstack([Gpva, Gpvv])]).real +
            vstack([hstack([Gqaa, Gqav]),
                    hstack([Gqva, Gqvv])]).imag,
            c_sparse((2 * nb, nxtra))]),
        hstack([
            c_sparse((nxtra, 2 * nb)),
            c_sparse((nxtra, nxtra))
        ])
    ], "csr")

    # ----- evaluate Hessian of flow constraints -----
    nmu = int(len(lmbda["ineqnonlin"]) / 2)
    muF = lmbda["ineqnonlin"][:nmu]
    muT = lmbda["ineqnonlin"][nmu:nmu + nmu]
    if ppopt['OPF_FLOW_LIM'] == 2:  # current
        dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = dIbr_dV(branch, Yf, Yt, V)
        Hfaa, Hfav, Hfva, Hfvv = d2AIbr_dV2(dIf_dVa, dIf_dVm, If, Yf, V, muF)
        Htaa, Htav, Htva, Htvv = d2AIbr_dV2(dIt_dVa, dIt_dVm, It, Yt, V, muT)
    else:
        f = branch[il, IDX.branch.F_BUS].astype(int)  # list of "from" buses
        t = branch[il, IDX.branch.T_BUS].astype(int)  # list of "to" buses
        # connection matrix for line & from buses
        Cf = c_sparse((np.ones(nl2), (np.arange(nl2), f)), (nl2, nb))
        # connection matrix for line & to buses
        Ct = c_sparse((np.ones(nl2), (np.arange(nl2), t)), (nl2, nb))
        dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = \
            dSbr_dV(branch[il, :], Yf, Yt, V)
        if ppopt['OPF_FLOW_LIM'] == 1:  # real power
            Hfaa, Hfav, Hfva, Hfvv = d2ASbr_dV2(dSf_dVa.real, dSf_dVm.real,
                                                Sf.real, Cf, Yf, V, muF)
            Htaa, Htav, Htva, Htvv = d2ASbr_dV2(dSt_dVa.real, dSt_dVm.real,
                                                St.real, Ct, Yt, V, muT)
        else:  # apparent power
            Hfaa, Hfav, Hfva, Hfvv = \
                d2ASbr_dV2(dSf_dVa, dSf_dVm, Sf, Cf, Yf, V, muF)
            Htaa, Htav, Htva, Htvv = \
                d2ASbr_dV2(dSt_dVa, dSt_dVm, St, Ct, Yt, V, muT)

    d2H = vstack([
        hstack([
            vstack([hstack([Hfaa, Hfav]),
                    hstack([Hfva, Hfvv])]) +
            vstack([hstack([Htaa, Htav]),
                    hstack([Htva, Htvv])]),
            c_sparse((2 * nb, nxtra))
        ]),
        hstack([
            c_sparse((nxtra, 2 * nb)),
            c_sparse((nxtra, nxtra))
        ])
    ], "csr")

    # -----  do numerical check using (central) finite differences  -----
    if 0:
        nx = len(x)
        step = 1e-5
        num_d2f = c_sparse((nx, nx))
        num_d2G = c_sparse((nx, nx))
        num_d2H = c_sparse((nx, nx))
        for i in range(nx):
            xp = x
            xm = x
            xp[i] = x[i] + step / 2
            xm[i] = x[i] - step / 2
            # evaluate cost & gradients
            _, dfp = opf_costfcn(xp, om)
            _, dfm = opf_costfcn(xm, om)
            # evaluate constraints & gradients
            _, _, dHp, dGp = opf_consfcn(xp, om, Ybus, Yf, Yt, ppopt, il)
            _, _, dHm, dGm = opf_consfcn(xm, om, Ybus, Yf, Yt, ppopt, il)
            num_d2f[:, i] = cost_mult * (dfp - dfm) / step
            num_d2G[:, i] = (dGp - dGm) * lmbda["eqnonlin"] / step
            num_d2H[:, i] = (dHp - dHm) * lmbda["ineqnonlin"] / step
        d2f_err = max(max(abs(d2f - num_d2f)))
        d2G_err = max(max(abs(d2G - num_d2G)))
        d2H_err = max(max(abs(d2H - num_d2H)))
        if d2f_err > 1e-6:
            print('Max difference in d2f: %g' % d2f_err)
        if d2G_err > 1e-5:
            print('Max difference in d2G: %g' % d2G_err)
        if d2H_err > 1e-6:
            print('Max difference in d2H: %g' % d2H_err)

    return d2f + d2G + d2H


def opf_consfcn(x, om, Ybus, Yf, Yt, ppopt, il=None, *args):
    """Evaluates nonlinear constraints and their Jacobian for OPF.

    Constraint evaluation function for AC optimal power flow, suitable
    for use with L{pips}. Computes constraint vectors and their gradients.

    @param x: optimization vector
    @param om: OPF model object
    @param Ybus: bus admittance matrix
    @param Yf: admittance matrix for "from" end of constrained branches
    @param Yt: admittance matrix for "to" end of constrained branches
    @param ppopt: PYPOWER options vector
    @param il: (optional) vector of branch indices corresponding to
    branches with flow limits (all others are assumed to be
    unconstrained). The default is C{range(nl)} (all branches).
    C{Yf} and C{Yt} contain only the rows corresponding to C{il}.

    @return: C{h} - vector of inequality constraint values (flow limits)
    limit^2 - flow^2, where the flow can be apparent power real power or
    current, depending on value of C{OPF_FLOW_LIM} in C{ppopt} (only for
    constrained lines). C{g} - vector of equality constraint values (power
    balances). C{dh} - (optional) inequality constraint gradients, column
    j is gradient of h(j). C{dg} - (optional) equality constraint gradients.

    @see: L{opf_costfcn}, L{opf_hessfcn}

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    """
    ##----- initialize -----

    ## unpack data
    ppc = om.get_ppc()
    baseMVA, bus, gen, branch = \
        ppc["baseMVA"], ppc["bus"], ppc["gen"], ppc["branch"]
    vv, _, _, _ = om.get_idx()

    ## problem dimensions
    nb = bus.shape[0]          ## number of buses
    nl = branch.shape[0]       ## number of branches
    ng = gen.shape[0]          ## number of dispatchable injections
    nxyz = len(x)              ## total number of control vars of all types

    ## set default constrained lines
    if il is None:
        il = arange(nl)         ## all lines have limits by default
    nl2 = len(il)              ## number of constrained lines

    ## grab Pg & Qg
    Pg = x[vv["i1"]["Pg"]:vv["iN"]["Pg"]]  ## active generation in p.u.
    Qg = x[vv["i1"]["Qg"]:vv["iN"]["Qg"]]  ## reactive generation in p.u.

    ## put Pg & Qg back in gen
    gen[:, PG] = Pg * baseMVA  ## active generation in MW
    gen[:, QG] = Qg * baseMVA  ## reactive generation in MVAr

    ## rebuild Sbus
    Sbus = makeSbus(baseMVA, bus, gen) ## net injected power in p.u.

    ## ----- evaluate constraints -----
    ## reconstruct V
    Va = x[vv["i1"]["Va"]:vv["iN"]["Va"]]
    Vm = x[vv["i1"]["Vm"]:vv["iN"]["Vm"]]
    V = Vm * exp(1j * Va)

    ## evaluate power flow equations
    mis = V * conj(Ybus * V) - Sbus

    ##----- evaluate constraint function values -----
    ## first, the equality constraints (power flow)
    g = r_[ mis.real,            ## active power mismatch for all buses
            mis.imag ]           ## reactive power mismatch for all buses

    ## then, the inequality constraints (branch flow limits)
    if nl2 > 0:
        flow_max = (branch[il, RATE_A] / baseMVA)**2
        flow_max[flow_max == 0] = Inf
        if ppopt['OPF_FLOW_LIM'] == 2:       ## current magnitude limit, |I|
            If = Yf * V
            It = Yt * V
            h = r_[ If * conj(If) - flow_max,     ## branch I limits (from bus)
                    It * conj(It) - flow_max ].real    ## branch I limits (to bus)
        else:
            ## compute branch power flows
            ## complex power injected at "from" bus (p.u.)
            Sf = V[ branch[il, F_BUS].astype(int) ] * conj(Yf * V)
            ## complex power injected at "to" bus (p.u.)
            St = V[ branch[il, T_BUS].astype(int) ] * conj(Yt * V)
            if ppopt['OPF_FLOW_LIM'] == 1:   ## active power limit, P (Pan Wei)
                h = r_[ Sf.real**2 - flow_max,   ## branch P limits (from bus)
                        St.real**2 - flow_max ]  ## branch P limits (to bus)
            else:                ## apparent power limit, |S|
                h = r_[ Sf * conj(Sf) - flow_max, ## branch S limits (from bus)
                        St * conj(St) - flow_max ].real  ## branch S limits (to bus)
    else:
        h = zeros((0,1))

    ##----- evaluate partials of constraints -----
    ## index ranges
    iVa = arange(vv["i1"]["Va"], vv["iN"]["Va"])
    iVm = arange(vv["i1"]["Vm"], vv["iN"]["Vm"])
    iPg = arange(vv["i1"]["Pg"], vv["iN"]["Pg"])
    iQg = arange(vv["i1"]["Qg"], vv["iN"]["Qg"])
    iVaVmPgQg = r_[iVa, iVm, iPg, iQg].T

    ## compute partials of injected bus powers
    dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)           ## w.r.t. V
    ## Pbus w.r.t. Pg, Qbus w.r.t. Qg
    neg_Cg = sparse((-ones(ng), (gen[:, GEN_BUS], range(ng))), (nb, ng))

    ## construct Jacobian of equality constraints (power flow) and transpose it
    dg = lil_matrix((2 * nb, nxyz))
    blank = sparse((nb, ng))
    dg[:, iVaVmPgQg] = vstack([
            ## P mismatch w.r.t Va, Vm, Pg, Qg
            hstack([dSbus_dVa.real, dSbus_dVm.real, neg_Cg, blank]),
            ## Q mismatch w.r.t Va, Vm, Pg, Qg
            hstack([dSbus_dVa.imag, dSbus_dVm.imag, blank, neg_Cg])
        ], "csr")
    dg = dg.T

    if nl2 > 0:
        ## compute partials of Flows w.r.t. V
        if ppopt['OPF_FLOW_LIM'] == 2:     ## current
            dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    dIbr_dV(branch[il, :], Yf, Yt, V)
        else:                  ## power
            dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    dSbr_dV(branch[il, :], Yf, Yt, V)
        if ppopt['OPF_FLOW_LIM'] == 1:     ## real part of flow (active power)
            dFf_dVa = dFf_dVa.real
            dFf_dVm = dFf_dVm.real
            dFt_dVa = dFt_dVa.real
            dFt_dVm = dFt_dVm.real
            Ff = Ff.real
            Ft = Ft.real

        ## squared magnitude of flow (of complex power or current, or real power)
        df_dVa, df_dVm, dt_dVa, dt_dVm = \
                dAbr_dV(dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft)

        ## construct Jacobian of inequality constraints (branch limits)
        ## and transpose it.
        dh = lil_matrix((2 * nl2, nxyz))
        dh[:, r_[iVa, iVm].T] = vstack([
                hstack([df_dVa, df_dVm]),    ## "from" flow limit
                hstack([dt_dVa, dt_dVm])     ## "to" flow limit
            ], "csr")
        dh = dh.T
    else:
        dh = None

    return h, g, dh, dg



def opf_costfcn(x, om, return_hessian=False):
    """Evaluates objective function, gradient and Hessian for OPF.

    Objective function evaluation routine for AC optimal power flow,
    suitable for use with L{pips}. Computes objective function value,
    gradient and Hessian.

    @param x: optimization vector
    @param om: OPF model object

    @return: C{F} - value of objective function. C{df} - (optional) gradient
    of objective function (column vector). C{d2f} - (optional) Hessian of
    objective function (sparse matrix).

    @see: L{opf_consfcn}, L{opf_hessfcn}

    @author: Carlos E. Murillo-Sanchez (PSERC Cornell & Universidad
    Autonoma de Manizales)
    @author: Ray Zimmerman (PSERC Cornell)
    """
    ##----- initialize -----
    ## unpack data
    ppc = om.get_ppc()
    baseMVA, gen, gencost = ppc["baseMVA"], ppc["gen"], ppc["gencost"]
    cp = om.get_cost_params()
    N, Cw, H, dd, rh, kk, mm = \
        cp["N"], cp["Cw"], cp["H"], cp["dd"], cp["rh"], cp["kk"], cp["mm"]
    vv, _, _, _ = om.get_idx()

    ## problem dimensions
    ng = gen.shape[0]          ## number of dispatchable injections
    ny = om.getN('var', 'y')   ## number of piece-wise linear costs
    nxyz = len(x)              ## total number of control vars of all types

    ## grab Pg & Qg
    Pg = x[vv["i1"]["Pg"]:vv["iN"]["Pg"]]  ## active generation in p.u.
    Qg = x[vv["i1"]["Qg"]:vv["iN"]["Qg"]]  ## reactive generation in p.u.

    ##----- evaluate objective function -----
    ## polynomial cost of P and Q
    # use totcost only on polynomial cost in the minimization problem
    # formulation, pwl cost is the sum of the y variables.
    ipol = find(gencost[:, MODEL] == POLYNOMIAL)   ## poly MW and MVAr costs
    xx = r_[ Pg, Qg ] * baseMVA
    if any(ipol):
        f = sum( totcost(gencost[ipol, :], xx[ipol]) )  ## cost of poly P or Q
    else:
        f = 0

    ## piecewise linear cost of P and Q
    if ny > 0:
        ccost = sparse((ones(ny),
                        (zeros(ny), arange(vv["i1"]["y"], vv["iN"]["y"]))),
                       (1, nxyz)).toarray().flatten()
        f = f + dot(ccost, x)
    else:
        ccost = zeros(nxyz)

    ## generalized cost term
    if issparse(N) and N.nnz > 0:
        nw = N.shape[0]
        r = N * x - rh                   ## Nx - rhat
        iLT = find(r < -kk)              ## below dead zone
        iEQ = find((r == 0) & (kk == 0)) ## dead zone doesn't exist
        iGT = find(r > kk)               ## above dead zone
        iND = r_[iLT, iEQ, iGT]          ## rows that are Not in the Dead region
        iL = find(dd == 1)           ## rows using linear function
        iQ = find(dd == 2)           ## rows using quadratic function
        LL = sparse((ones(len(iL)), (iL, iL)), (nw, nw))
        QQ = sparse((ones(len(iQ)), (iQ, iQ)), (nw, nw))
        kbar = sparse((r_[ones(len(iLT)), zeros(len(iEQ)), -ones(len(iGT))],
                       (iND, iND)), (nw, nw)) * kk
        rr = r + kbar                  ## apply non-dead zone shift
        M = sparse((mm[iND], (iND, iND)), (nw, nw))  ## dead zone or scale
        diagrr = sparse((rr, (arange(nw), arange(nw))), (nw, nw))

        ## linear rows multiplied by rr(i), quadratic rows by rr(i)^2
        w = M * (LL + QQ * diagrr) * rr

        f = f + dot(w * H, w) / 2 + dot(Cw, w)

    ##----- evaluate cost gradient -----
    ## index ranges
    iPg = range(vv["i1"]["Pg"], vv["iN"]["Pg"])
    iQg = range(vv["i1"]["Qg"], vv["iN"]["Qg"])

    ## polynomial cost of P and Q
    df_dPgQg = zeros(2 * ng)        ## w.r.t p.u. Pg and Qg
    df_dPgQg[ipol] = baseMVA * polycost(gencost[ipol, :], xx[ipol], 1)
    df = zeros(nxyz)
    df[iPg] = df_dPgQg[:ng]
    df[iQg] = df_dPgQg[ng:ng + ng]

    ## piecewise linear cost of P and Q
    df = df + ccost  # The linear cost row is additive wrt any nonlinear cost.

    ## generalized cost term
    if issparse(N) and N.nnz > 0:
        HwC = H * w + Cw
        AA = N.T * M * (LL + 2 * QQ * diagrr)
        df = df + AA * HwC

        ## numerical check
        if 0:    ## 1 to check, 0 to skip check
            ddff = zeros(df.shape)
            step = 1e-7
            tol  = 1e-3
            for k in range(len(x)):
                xx = x
                xx[k] = xx[k] + step
                ddff[k] = (opf_costfcn(xx, om) - f) / step
            if max(abs(ddff - df)) > tol:
                idx = find(abs(ddff - df) == max(abs(ddff - df)))
                print('Mismatch in gradient')
                print('idx             df(num)         df              diff')
                print('%4d%16g%16g%16g' %
                      (range(len(df)), ddff.T, df.T, abs(ddff - df).T))
                print('MAX')
                print('%4d%16g%16g%16g' %
                      (idx.T, ddff[idx].T, df[idx].T,
                       abs(ddff[idx] - df[idx]).T))

    if not return_hessian:
        return f, df

    ## ---- evaluate cost Hessian -----
    pcost = gencost[range(ng), :]
    if gencost.shape[0] > ng:
        qcost = gencost[ng + 1:2 * ng, :]
    else:
        qcost = array([])

    ## polynomial generator costs
    d2f_dPg2 = zeros(ng)               ## w.r.t. p.u. Pg
    d2f_dQg2 = zeros(ng)               ## w.r.t. p.u. Qg
    ipolp = find(pcost[:, MODEL] == POLYNOMIAL)
    d2f_dPg2[ipolp] = \
            baseMVA**2 * polycost(pcost[ipolp, :], Pg[ipolp]*baseMVA, 2)
    if any(qcost):          ## Qg is not free
        ipolq = find(qcost[:, MODEL] == POLYNOMIAL)
        d2f_dQg2[ipolq] = \
                baseMVA**2 * polycost(qcost[ipolq, :], Qg[ipolq] * baseMVA, 2)
    i = r_[iPg, iQg].T
    d2f = sparse((r_[d2f_dPg2, d2f_dQg2], (i, i)), (nxyz, nxyz))

    ## generalized cost
    if N is not None and issparse(N):
        d2f = d2f + AA * H * AA.T + 2 * N.T * M * QQ * \
                sparse((HwC, (range(nw), range(nw))), (nw, nw)) * N

    return f, df, d2f


def run_userfcn(userfcn, stage, *args2):
    """Runs the userfcn callbacks for a given stage.

    Example::
        ppc = om.get_mpc()
        om = run_userfcn(ppc['userfcn'], 'formulation', om)

    @param userfcn: the 'userfcn' field of ppc, populated by L{add_userfcn}
    @param stage: the name of the callback stage begin executed
    (additional arguments) some stages require additional arguments.

    @see: L{add_userfcn}, L{remove_userfcn}, L{toggle_reserves},
          L{toggle_iflims}, L{runopf_w_res}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    rv = args2[0]
    if (len(userfcn) > 0) and (stage in userfcn):
        for k in range(len(userfcn[stage])):
            if 'args' in userfcn[stage][k]:
                args = userfcn[stage][k]['args']
            else:
                args = []

            if stage in ['ext2int', 'formulation', 'int2ext']:
                # ppc     = userfcn_*_ext2int(ppc, args)
                # om      = userfcn_*_formulation(om, args)
                # results = userfcn_*_int2ext(results, args)
                rv = userfcn[stage][k]['fcn'](rv, args)
            elif stage in ['printpf', 'savecase']:
                # results = userfcn_*_printpf(results, fd, ppopt, args)
                # ppc     = userfcn_*_savecase(mpc, fd, prefix, args)
                fdprint = args2[1]
                ppoptprint = args2[2]
                rv = userfcn[stage][k]['fcn'](rv, fdprint, ppoptprint, args)

    return rv



def add_userfcn(ppc, stage, fcn, args=None, allow_multiple=False):
    """Appends a userfcn to the list to be called for a case.

    A userfcn is a callback function that can be called automatically by
    PYPOWER at one of various stages in a simulation.

    Currently there are 5 different callback stages defined. Each stage has
    a name, and by convention, the name of a user-defined callback function
    ends with the name of the stage. The following is a description of each
    stage, when it is called and the input and output arguments which vary
    depending on the stage. The reserves example (see L{runopf_w_res}) is used
    to illustrate how these callback userfcns might be used.

      1. C{'ext2int'}

      Called from L{ext2int} immediately after the case is converted from
      external to internal indexing. Inputs are a PYPOWER case dict (C{ppc}),
      freshly converted to internal indexing and any (optional) C{args} value
      supplied via L{add_userfcn}. Output is the (presumably updated) C{ppc}.
      This is typically used to reorder any input arguments that may be needed
      in internal ordering by the formulation stage.

      E.g. C{ppc = userfcn_reserves_ext2int(ppc, args)}

      2. C{'formulation'}

      Called from L{opf} after the OPF Model (C{om}) object has been
      initialized with the standard OPF formulation, but before calling the
      solver. Inputs are the C{om} object and any (optional) C{args} supplied
      via L{add_userfcn}. Output is the C{om} object. This is the ideal place
      to add any additional vars, constraints or costs to the OPF formulation.

      E.g. C{om = userfcn_reserves_formulation(om, args)}

      3. C{'int2ext'}

      Called from L{int2ext} immediately before the resulting case is converted
      from internal back to external indexing. Inputs are the C{results} dict
      and any (optional) C{args} supplied via C{add_userfcn}. Output is the
      C{results} dict. This is typically used to convert any results to
      external indexing and populate any corresponding fields in the
      C{results} dict.

      E.g. C{results = userfcn_reserves_int2ext(results, args)}

      4. C{'printpf'}

      Called from L{printpf} after the pretty-printing of the standard OPF
      output. Inputs are the C{results} dict, the file descriptor to write to,
      a PYPOWER options dict, and any (optional) C{args} supplied via
      L{add_userfcn}. Output is the C{results} dict. This is typically used for
      any additional pretty-printing of results.

      E.g. C{results = userfcn_reserves_printpf(results, fd, ppopt, args)}

      5. C{'savecase'}

      Called from L{savecase} when saving a case dict to a Python file after
      printing all of the other data to the file. Inputs are the case dict,
      the file descriptor to write to, the variable prefix (typically 'ppc')
      and any (optional) C{args} supplied via L{add_userfcn}. Output is the
      case dict. This is typically used to write any non-standard case dict
      fields to the case file.

      E.g. C{ppc = userfcn_reserves_printpf(ppc, fd, prefix, args)}

    @param ppc: the case dict
    @param stage: the name of the stage at which this function should be
        called: ext2int, formulation, int2ext, printpf
    @param fcn: the name of the userfcn
    @param args: (optional) the value to be passed as an argument to the
        userfcn
    @param allow_multiple: (optional) if True, allows the same function to
        be added more than once.

    @see: L{run_userfcn}, L{remove_userfcn}, L{toggle_reserves},
          L{toggle_iflims}, L{runopf_w_res}.

    @author: Ray Zimmerman (PSERC Cornell)
    """
    if args is None:
        args = []

    if stage not in ['ext2int', 'formulation', 'int2ext', 'printpf', 'savecase']:
        logger.debug('add_userfcn : \'%s\' is not the name of a valid callback stage\n' % stage)

    n = 0
    if 'userfcn' in ppc:
        if stage in ppc['userfcn']:
            n = len(ppc['userfcn'][stage])  # + 1
            if not allow_multiple:
                for k in range(n):
                    if ppc['userfcn'][stage][k]['fcn'] == fcn:
                        logger.debug('add_userfcn: the function \'%s\' has already been added\n' % fcn.__name__)
        else:
            ppc['userfcn'][stage] = []
    else:
        ppc['userfcn'] = {stage: []}

    ppc['userfcn'][stage].append({'fcn': fcn})
    if len(args) > 0:
        ppc['userfcn'][stage][n]['args'] = args

    return ppc

def remove_userfcn(ppc, stage, fcn):
    """Removes a userfcn from the list to be called for a case.

    A userfcn is a callback function that can be called automatically by
    PYPOWER at one of various stages in a simulation. This function removes
    the last instance of the userfcn for the given C{stage} with the function
    handle specified by C{fcn}.

    @see: L{add_userfcn}, L{run_userfcn}, L{toggle_reserves},
          L{toggle_iflims}, L{runopf_w_res}

    @author: Ray Zimmerman (PSERC Cornell)
    """
    n = len(ppc['userfcn'][stage])

    for k in range(n - 1, -1, -1):
        if ppc['userfcn'][stage][k]['fcn'] == fcn:
            del ppc['userfcn'][stage][k]
            break

    return ppc

