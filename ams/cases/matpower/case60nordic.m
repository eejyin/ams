function mpc = case60nordic
%CASE60NORDIC   60-bus Nordic case, by Florin Capitanescu
%   These data stem from and extend the Nordic32 test system initially
%   developed by CIGRE Task Force 38.02.08, "Long-term dynamics, phase II"
%   in 1995. These data were further enriched in the research group of
%   Thierry Van Cutsem. My further derivation leading to this test case
%   consists in: (i) enriching the data set with OPF-related data (physical
%   limits, cost functions), (ii) definition of various AC OPF/SCOPF
%   problems presented in many of my papers, and (iii) data conversion from
%   initial format to my OPF data format and then to MATPOWER (.m) format.
%
%   This power system model contains 60 buses, 23 generators, 57 lines,
%   31 transformers (out of which 8 OLTCs, the last 8 branch records),
%   22 loads, and 12 shunt elements.
%
%   These specific data sets served me to solve various instances of AC
%   OPF/SCOPF problems with different objective functions, sets of decision
%   variables (e.g. among: generators active/reactive powers, ratio of LTC
%   transformers, reactance of shunt capacitors/reactors) and constraints.
%   Some of the OPF results can be found at:
%       https://people.montefiore.uliege.be/capitane/
%
%   If you wish to include control variables like transformer ratio and
%   shunt reactance or N-1 contingencies, please contact me to share with
%   you their associated data. In my AC OPF formulations all thermal
%   limits were expressed only in terms of current.
%
%   When publishing results based on these data, please cite:
%
%       F. Capitanescu, "Suppressing ineffective control actions in optimal
%       power flow problems", IET Generation, Transmission & Distribution
%       14 (13), pp. 2520-2527, 2020.
%       doi: 10.1049/iet-gtd.2019.1783
%
%   Contact: Florin Capitanescu fcapitanescu@yahoo.com
%
%   February 19th, 2021

%   MATPOWER
%   Copyright (c) 2021 by Florin Capitanescu
%   Licensed under the Creative Commons Attribution 4.0 International license,
%   https://creativecommons.org/licenses/by/4.0/

%% MATPOWER Case Format : Version 2
mpc.version = '2';

%%-----  Power Flow Data  -----%%
%% system MVA base
mpc.baseMVA = 100;

%% bus data
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
mpc.bus = [
	1	1	200	80	0	-340.12	1	1.064082	-15.563001	130	1	1.1	0.9;
	2	1	300	100	0	0	1	1.083567	-14.09203	130	1	1.1	0.9;
	3	1	100	40	0	0	1	1.058654	-10.182816	130	1	1.1	0.9;
	4	1	280	95	0	150	1	1.096596	-17.7009	130	1	1.1	0.9;
	5	1	402.2198	190.111	0	200	1	1.053068	-41.503713	130	1	1.1	0.9;
	6	1	201.2099	75.06049	0	0	1	1.045071	-28.663263	130	1	1.1	0.9;
	7	1	154.2076	96.21037	0	100	1	1.057085	-37.808583	130	1	1.1	0.9;
	8	1	536.4263	286.8214	0	200	1	1.061996	-33.606318	130	1	1.1	0.9;
	9	1	469.4231	238.4712	0	200	1	1.067548	-36.331543	130	1	1.1	0.9;
	10	1	100	30	0	0	1	1.079598	-22.844109	220	1	1.1	0.9;
	11	1	200	50	0	0	1	1.018959	-15.053383	220	1	1.1	0.9;
	12	1	300	100	0	-400	1	0.991571	-26.531716	400	1	1.1	0.9;
	13	1	2000	500	0	0	1	1.004524	-32.784826	400	1	1.1	0.9;
	14	1	362.0178	151.1009	0	200	1	1.08107	-32.180729	400	1	1.1	0.9;
	15	1	268.2132	143.4107	0	0	1	1.060573	-28.088084	400	1	1.1	0.9;
	16	1	603.4296	288.1715	0	200	1	1.045303	-28.404205	400	1	1.1	0.9;
	17	1	469.4231	238.4712	0	100	1	1.031922	-26.304401	400	1	1.1	0.9;
	18	1	67.0033	48.35017	0	0	1	1.036064	-19.430476	400	1	1.1	0.9;
	19	1	536.4263	288.8214	0	100	1	1.046955	-33.337959	400	1	1.1	0.9;
	20	1	500	149	0	0	1	1.025557	-40.764411	400	1	1.1	0.9;
	21	1	300	100	0	0	1	1.028314	-39.398039	400	1	1.1	0.9;
	22	1	590	300	0	0	1	1.013333	-39.21771	400	1	1.1	0.9;
	23	1	0	0	0	-100	1	0.985738	-15.214764	400	1	1.1	0.9;
	24	1	0	0	0	0	1	1.067034	-8.648865	130	1	1.1	0.9;
	25	1	0	0	0	0	1	1.07502	-2.638356	130	1	1.1	0.9;
	26	1	0	0	0	0	1	0.986067	-15.919696	400	1	1.1	0.9;
	27	1	0	0	0	0	1	1.068863	-21.576377	400	1	1.1	0.9;
	28	1	0	0	0	0	1	1.032869	-18.827698	400	1	1.1	0.9;
	29	1	0	0	0	0	1	1.068559	-25.255516	400	1	1.1	0.9;
	30	1	0	0	0	0	1	0.978794	-32.626173	400	1	1.1	0.9;
	31	1	0	0	0	0	1	1.053472	-24.01627	400	1	1.1	0.9;
	32	1	0	0	0	0	1	1.049524	-39.582141	400	1	1.1	0.9;
	33	1	0	0	0	0	1	1.049524	-39.582141	400	1	1.1	0.9;
	34	1	0	0	0	0	1	1.020882	-30.156834	400	1	1.1	0.9;
	35	1	0	0	0	0	1	1.021283	-35.89561	400	1	1.1	0.9;
	36	1	0	0	0	0	1	1.065873	-31.893982	400	1	1.1	0.9;
	37	1	0	0	0	0	1	1.06957	-34.842542	400	1	1.1	0.9;
	38	2	0	0	0	0	1	1.07	-10.727834	15	1	1.1	0.9;
	39	2	0	0	0	0	1	1.055	-6.69034	15	1	1.1	0.9;
	40	2	0	0	0	0	1	1.06	-4.765096	15	1	1.1	0.9;
	41	2	0	0	0	0	1	1.07	1.126925	15	1	1.1	0.9;
	42	2	0	0	0	0	1	1.07	-12.172581	15	1	1.1	0.9;
	43	2	0	0	0	0	1	1.063348	-22.570252	15	1	1.1	0.9;
	44	2	0	0	0	0	1	1.05399	-30.566378	15	1	1.1	0.9;
	45	2	0	0	0	0	1	1.0042	-10.001941	15	1	1.1	0.9;
	46	2	0	0	0	0	1	0.9989	-12.116254	15	1	1.1	0.9;
	47	2	0	0	0	0	1	1.0019	-10.828162	15	1	1.1	0.9;
	48	2	0	0	0	0	1	1.0336	-15.443018	15	1	1.1	0.9;
	49	2	0	0	0	0	1	1.0141	-17.248593	15	1	1.1	0.9;
	50	2	0	0	0	0	1	1	-32.180757	15	1	1.1	0.9;
	51	2	0	0	0	0	1	1.0113	-24.187821	15	1	1.1	0.9;
	52	3	0	0	0	0	1	1.0611	0	15	1	1.1	0.9;
	53	2	0	0	0	0	1	1.0611	-15.560206	15	1	1.1	0.9;
	54	2	0	0	0	0	1	1.0447	-29.738419	15	1	1.1	0.9;
	55	2	0	0	0	0	1	1.0369	-29.376407	15	1	1.1	0.9;
	56	2	0	0	0	0	1	1.0116	-35.252215	15	1	1.1	0.9;
	57	2	0	0	0	0	1	1.029	-35.081723	15	1	1.1	0.9;
	58	2	0	0	0	0	1	1.029	-35.081723	15	1	1.1	0.9;
	59	2	0	0	0	0	1	1.03	-22.374519	15	1	1.1	0.9;
	60	2	0	0	0	0	1	1.0185	-30.364105	15	1	1.1	0.9;
];

%% generator data
%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
mpc.gen = [
	38	362.8692	-66.767236	720	-720	1.07	800	1	720	10	0	0	0	0	0	0	0	0	0	0	0;
	39	272.1519	-7.123284	540	-540	1.055	600	1	540	10	0	0	0	0	0	0	0	0	0	0	0;
	40	357.5106	-22.670573	630	-630	1.06	700	1	630	10	0	0	0	0	0	0	0	0	0	0	0;
	41	302.1519	-11.549816	540	-540	1.07	600	1	540	10	0	0	0	0	0	0	0	0	0	0	0;
	42	188.3966	-38.335054	325	-225	1.07	400	1	475	10	0	0	0	0	0	0	0	0	0	0	0;
	43	314.5454	68.564837	560	-360	1.063348	600	1	560	10	0	0	0	0	0	0	0	0	0	0	0;
	44	187.2727	7.501724	360	-280	1.05399	400	1	380	10	0	0	0	0	0	0	0	0	0	0	0;
	45	510.5485	-61.467132	965	-765	1.0042	1000	1	965	10	0	0	0	0	0	0	0	0	0	0	0;
	46	435.5865	99.922135	900	-900	0.9989	1000	1	900	10	0	0	0	0	0	0	0	0	0	0	0;
	47	402.8692	101.789384	720	-720	1.0019	800	1	720	10	0	0	0	0	0	0	0	0	0	0	0;
	48	236.0759	-60.248316	570	-370	1.0336	600	1	570	10	0	0	0	0	0	0	0	0	0	0	0;
	49	293.7553	-75.795423	515	-415	1.0141	600	1	575	10	0	0	0	0	0	0	0	0	0	0	0;
	50	0	-243.210921	570	-570	1	600	1	0	0	0	0	0	0	0	0	0	0	0	0	0;
	51	340.4546	-220.947271	630	-630	1.0113	700	1	630	10	0	0	0	0	0	0	0	0	0	0	0;
	52	1462.87562	356.714649	1840	-540	1.0611	3000	1	2800	10	0	0	0	0	0	0	0	0	0	0	0;
	53	296.8182	116.288946	580	-540	1.0611	600	1	540	10	0	0	0	0	0	0	0	0	0	0	0;
	54	320.4545	-0.927939	630	-630	1.0447	700	1	630	10	0	0	0	0	0	0	0	0	0	0	0;
	55	350	-36.553736	630	-630	1.0369	700	1	630	10	0	0	0	0	0	0	0	0	0	0	0;
	56	300.8182	-56.742588	540	-540	1.0116	600	1	540	10	0	0	0	0	0	0	0	0	0	0	0;
	57	300.8182	75.346059	540	-540	1.029	600	1	540	10	0	0	0	0	0	0	0	0	0	0	0;
	58	300.8182	75.346059	540	-540	1.029	600	1	540	10	0	0	0	0	0	0	0	0	0	0	0;
	59	246.7932	140.896249	520	-450	1.03	600	1	560	10	0	0	0	0	0	0	0	0	0	0	0;
	60	1296.3868	454.44114	4000	-2050	1.0185	5000	1	4500	10	0	0	0	0	0	0	0	0	0	0	0;
];

%% branch data
%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax
mpc.branch = [
	1	3	0.01	0.07	0.013804	175	175	175	0	0	1	-360	360;
	1	3	0.01	0.07	0.013804	175	175	175	0	0	1	-360	360;
	2	24	0.014024	0.09	0.018052	175	175	175	0	0	1	-360	360;
	2	24	0.014024	0.09	0.018052	175	175	175	0	0	1	-360	360;
	3	24	0.006982	0.05	0.010088	175	175	175	0	0	1	-360	360;
	3	24	0.006982	0.05	0.010088	175	175	175	0	0	1	-360	360;
	25	4	0.03	0.2	0.030263	175	175	175	0	0	1	-360	360;
	25	4	0.03	0.2	0.030263	175	175	175	0	0	1	-360	360;
	5	7	0.01	0.06	0.012211	175	175	175	0	0	1	-360	360;
	5	7	0.01	0.06	0.012211	175	175	175	0	0	1	-360	360;
	5	9	0.01497	0.12	0.024954	175	175	175	0	0	1	-360	360;
	5	9	0.01497	0.12	0.024954	175	175	175	0	0	1	-360	360;
	6	8	0.037988	0.28	0.059995	175	175	175	0	0	1	-360	360;
	6	8	0.037988	0.28	0.059995	175	175	175	0	0	1	-360	360;
	6	9	0.05	0.3	0.059995	175	175	175	0	0	1	-360	360;
	7	8	0.01	0.08	0.015928	175	175	175	0	0	1	-360	360;
	7	8	0.01	0.08	0.015928	175	175	175	0	0	1	-360	360;
	10	11	0.012004	0.09	0.015205	250	250	250	0	0	1	-360	360;
	10	11	0.012004	0.09	0.015205	250	250	250	0	0	1	-360	360;
	26	23	0.001	0.008	0.201062	700	700	700	0	0	1	-360	360;
	26	27	0.006	0.06	1.799488	700	700	700	0	0	1	-360	360;
	26	28	0.004	0.04	1.201344	700	700	700	0	0	1	-360	360;
	26	12	0.005	0.045	1.4024	700	700	700	0	0	1	-360	360;
	23	28	0.004	0.035	1.05056	700	700	700	0	0	1	-360	360;
	23	12	0.005	0.05	1.49792	700	700	700	0	0	1	-360	360;
	27	29	0.004	0.04	1.201344	700	700	700	0	0	1	-360	360;
	27	30	0.01	0.1	3.000864	700	700	700	0	0	1	-360	360;
	30	15	0	-0.04	0	700	700	700	0	0	1	-360	360;
	28	31	0.004	0.04	1.201344	700	700	700	0	0	1	-360	360;
	28	31	0.004	0.04	1.201344	700	700	700	0	0	1	-360	360;
	31	29	0.001	0.01	0.301594	700	700	700	0	0	1	-360	360;
	31	32	0.006	0.08	2.397664	700	700	700	0	0	1	-360	360;
	32	14	0	-0.04	0	700	700	700	0	0	1	-360	360;
	31	33	0.006	0.08	2.397664	700	700	700	0	0	1	-360	360;
	33	14	0	-0.04	0	700	700	700	0	0	1	-360	360;
	29	34	0.01	0.066669	2.000576	700	700	700	0	0	1	-360	360;
	34	15	0	-0.026669	0	700	700	700	0	0	1	-360	360;
	29	35	0.006	0.08	2.397664	700	700	700	0	0	1	-360	360;
	35	36	0	-0.03	0	700	700	700	0	0	1	-360	360;
	14	36	0.003	0.03	0.899744	700	700	700	0	0	1	-360	360;
	14	20	0.006	0.045	1.301888	700	700	700	0	0	1	-360	360;
	15	16	0.002	0.015	0.497632	700	700	700	0	0	1	-360	360;
	15	36	0.002	0.02	0.598176	700	700	700	0	0	1	-360	360;
	16	36	0.001	0.01	0.301594	700	700	700	0	0	1	-360	360;
	16	17	0.001	0.01	0.301594	700	700	700	0	0	1	-360	360;
	16	18	0.002	0.02	0.598176	700	700	700	0	0	1	-360	360;
	36	37	0.002	0.02	0.598176	700	700	700	0	0	1	-360	360;
	36	37	0.002	0.02	0.598176	700	700	700	0	0	1	-360	360;
	37	19	0.004	0.04	1.201344	700	700	700	0	0	1	-360	360;
	37	19	0.004	0.04	1.201344	700	700	700	0	0	1	-360	360;
	37	21	0.011	0.08	2.397664	700	700	700	0	0	1	-360	360;
	17	18	0.001	0.015	0.497632	700	700	700	0	0	1	-360	360;
	20	21	0.002	0.02	0.598176	700	700	700	0	0	1	-360	360;
	21	22	0.003	0.03	0.899744	700	700	700	0	0	1	-360	360;
	21	22	0.003	0.03	0.899744	700	700	700	0	0	1	-360	360;
	12	13	0.003	0.03	3.000864	700	700	700	0	0	1	-360	360;
	12	13	0.003	0.03	3.000864	700	700	700	0	0	1	-360	360;
	2	38	0	0.01875	0	800	800	800	1	0	1	-360	360;
	3	39	0	0.025	0	600	600	600	1	0	1	-360	360;
	24	40	0	0.021429	0	700	700	700	1	0	1	-360	360;
	25	41	0	0.025	0	600	600	600	1	0	1	-360	360;
	4	42	0	0.06	0	1250	1250	1250	1	0	1	-360	360;
	6	43	0	0.0375	0	400	400	400	1	0	1	-360	360;
	7	44	0	0.075	0	1200	1200	1200	1	0	1	-360	360;
	11	45	0	0.017647	0	850	850	850	1	0	1	-360	360;
	26	46	0	0.015	0	1000	1000	1000	1	0	1	-360	360;
	23	47	0	0.01875	0	800	800	800	1	0	1	-360	360;
	27	48	0	0.05	0	300	300	300	1	0	1	-360	360;
	31	49	0	0.042857	0	1350	1350	1350	1	0	1	-360	360;
	14	50	0	0.033333	0	300	300	300	1	0	1	-360	360;
	15	51	0	0.021429	0	700	700	700	1	0	1	-360	360;
	18	52	0	0.025	0	600	600	600	1	0	1	-360	360;
	18	53	0	0.025	0	600	600	600	1	0	1	-360	360;
	19	54	0	0.021429	0	700	700	700	1	0	1	-360	360;
	19	55	0	0.021429	0	700	700	700	1	0	1	-360	360;
	21	56	0	0.025	0	600	600	600	1	0	1	-360	360;
	22	57	0	0.025	0	600	600	600	1	0	1	-360	360;
	22	58	0	0.025	0	600	600	600	1	0	1	-360	360;
	12	59	0	0.03	0	500	500	500	1	0	1	-360	360;
	13	60	0	0.003333	0	4500	4500	4500	1	0	1	-360	360;
	26	1	0	0.008	0	1250	1250	1250	0.89286	0	1	-360	360;
	23	2	0	0.008	0	1250	1250	1250	0.89286	0	1	-360	360;
	28	4	0	0.012	0	833.3	833.3	833.3	0.93458	0	1	-360	360;
	31	10	0	0.012	0	833.3	833.3	833.3	0.95238	0	1	-360	360;
	36	8	0	0.01	0	1000	1000	1000	1	0	1	-360	360;
	36	8	0	0.01	0	1000	1000	1000	1	0	1	-360	360;
	37	9	0	0.01	0	1000	1000	1000	1	0	1	-360	360;
	37	9	0	0.01	0	1000	1000	1000	1	0	1	-360	360;
];

%%-----  OPF Data  -----%%
%% generator cost data
%	1	startup	shutdown	n	x1	y1	...	xn	yn
%	2	startup	shutdown	n	c(n-1)	...	c0
mpc.gencost = [
	2	0	0	3	0	1	0;
	2	0	0	3	0	2	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	3	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	2	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	3	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	2	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	3	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	2	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	3	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	2	0;
	2	0	0	3	0	1	0;
	2	0	0	3	0	3	0;
	2	0	0	3	0	1	0;
];