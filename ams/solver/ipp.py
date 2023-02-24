"""
Interface to PYPOWER
"""
import logging

from collections import OrderedDict  # NOQA

from numpy import array  # NOQA
import pandas as pd  # NOQA

logger = logging.getLogger(__name__)


def load_ppc(case) -> dict:
    """
    Load PYPOWER case file into a dict.

    Parameters
    ----------
    case : str
        The path to the PYPOWER case file.

    Returns
    -------
    ppc : dict
        The PYPOWER case dict.
    """
    exec(open(f"{case}").read())
    # NOTE: the following line is not robust
    func_name = case.split('/')[-1].rstrip('.py')
    ppc = eval(f"{func_name}()")
    source_type = 'ppc'
    return ppc


def to_ppc(ssp) -> dict:
    """
    Convert the AMS system to a PYPOWER case dict.

    Parameters
    ----------
    ssp : ams.system
        The AMS system.

    Returns
    -------
    ppc : dict
        The PYPOWER case dict.
    key_dict : OrderedDict
        Mapping dict between AMS system and PYPOWER.
    """
    # TODO: convert the AMS system to a PYPOWER case dict

    if not ssp.is_setup:
        logger.warning('System has not been setup. Conversion aborted.')
        return None

    key_dict = OrderedDict()

    # --- initialize ppc ---
    ppc = {"version": '2'}
    mva = ssp.config.mva  # system MVA base
    ppc["baseMVA"] = mva

    # --- bus data ---
    ssp_bus = ssp.Bus.as_df().rename(columns={'idx': 'bus'}).reset_index(drop=True)
    key_dict['Bus'] = OrderedDict(
        {ssp: ppc for ssp, ppc in enumerate(ssp_bus['bus'].tolist(), start=1)})

    # NOTE: bus data: bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    # NOTE: bus type, 1 = PQ, 2 = PV, 3 = ref, 4 = isolated
    bus_cols = ['bus_i', 'type', 'Pd', 'Qd', 'Gs', 'Bs', 'area', 'Vm', 'Va',
                'baseKV', 'zone', 'Vmax', 'Vmin']
    ppc_bus = pd.DataFrame(columns=bus_cols)

    ppc_bus['bus_i'] = key_dict['Bus'].values()
    ppc_bus['type'] = 1  # default to PQ bus
    # TODO: add check for isolated buses

    # load data
    ssp_pq = ssp.PQ.as_df()
    ssp_pq[['p0', 'q0']] = ssp_pq[['p0', 'q0']].mul(mva)
    ppc_load = pd.merge(ssp_bus,
                        ssp_pq[['bus', 'p0', 'q0']].rename(columns={'p0': 'Pd', 'q0': 'Qd'}),
                        on='bus', how='left').fillna(0)
    ppc_bus[['Pd', 'Qd']] = ppc_load[['Pd', 'Qd']]

    # shunt data
    ssp_shunt = ssp.Shunt.as_df()
    ssp_shunt['g'] = ssp_shunt['g'] * ssp_shunt['u']
    ssp_shunt['b'] = ssp_shunt['b'] * ssp_shunt['u']
    ssp_shunt[['g', 'b']] = ssp_shunt[['g', 'b']] * mva
    ppc_y = pd.merge(ssp_bus,
                     ssp_shunt[['bus', 'g', 'b']].rename(columns={'g': 'Gs', 'b': 'Bs'}),
                     on='bus', how='left').fillna(0)
    ppc_bus[['Gs', 'Bs']] = ppc_y[['Gs', 'Bs']]

    # rest of the bus data
    ppc_bus_cols = ['area', 'Vm', 'Va', 'baseKV', 'zone', 'Vmax', 'Vmin']
    ssp_bus_cols = ['area', 'v0', 'a0', 'Vn', 'owner', 'vmax', 'vmin']
    ppc_bus[ppc_bus_cols] = ssp_bus[ssp_bus_cols]

    # --- generator data ---
    pv_df = ssp.PV.as_df()
    slack_df = ssp.Slack.as_df()
    gen_df = pd.concat([pv_df, slack_df], ignore_index=True)
    key_dict['Slack'] = OrderedDict(
        {ssp: ppc for ssp, ppc in enumerate(slack_df['idx'].tolist(), start=1)})
    key_dict['PV'] = OrderedDict(
        {ssp: ppc for ssp, ppc in enumerate(pv_df['idx'].tolist(), start=1)})

    # NOTE: gen data:
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
    # Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
    gen_cols = ['bus', 'Pg', 'Qg', 'Qmax', 'Qmin', 'Vg', 'mBase', 'status',
                'Pmax', 'Pmin', 'Pc1', 'Pc2',
                'Qc1min', 'Qc1max', 'Qc2min', 'Qc2max',
                'ramp_agc', 'ramp_10', 'ramp_30', 'ramp_q', 'apf']
    ppc_gen = pd.DataFrame(columns=gen_cols)

    # bus idx in ppc
    gen_bus_ppc = [key_dict['Bus'][bus_idx] for bus_idx in gen_df['bus'].tolist()]
    ppc_gen['bus'] = gen_bus_ppc
    # data that needs to be converted
    dcols = OrderedDict([
        ('Pg', 'p0'), ('Qg', 'q0'), ('Qmax', 'qmax'), ('Qmin', 'qmin'),
        ('Pmax', 'pmax'), ('Pmin', 'pmin'), ('ramp_agc', 'Ragc'),
        ('ramp_10', 'R10'), ('ramp_30', 'R30'), ('ramp_q', 'Rq')
    ])
    scols = ['Pc1', 'Pc2', 'Qc1min', 'Qc1max', 'Qc2min', 'Qc2max', 'apf']
    ppc_gen[list(dcols.keys())] = gen_df[list(dcols.values())].mul(mva)
    ppc_gen[scols] = gen_df[scols].mul(mva)
    ppc_gen['Vg'] = gen_df['v0']

    # rest of the gen data
    ppc_gen[['mBase', 'status', 'Vg']] = gen_df[['Sn', 'u', 'v0']]

    # branch

    # areas

    # gencost

    # --- output ---
    ppc["bus"] = ppc_bus.values
    ppc["gen"] = ppc_gen.values

    return ppc, key_dict, ppc_bus, ppc_gen
