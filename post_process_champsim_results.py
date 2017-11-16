# !/usr/sup/bin/python
# post_process_champsim_results.py
# Behnam Heydarshahi, November 2017
# Tufts Computer Architecture Lab
#
# This program reads champsim output files and plots them (mpki and ipc)

# FIXME: This should ideally be done through settings, not here in code
import os

from graphics.plot import plot_y_with_stderr, barchart, barchart_dual_y_shared_x
from graphics.subplotable import SubPlotable
from model.champ_sim_result import ChampSimResult
from model.core_perf import LLC_TOTAL_LINE_POSITION_RELATIVE_TO_CORE, extract_ipc_and_instruction_count, \
    extract_llc_misses, CorePerf

#os.environ["DISPLAY"] = "localhost:16.0"

import sys
import re
import datetime
import numpy
import csv
from collections import defaultdict
from math import log
from operator import add
from operator import truediv

# import matplotlib
# matplotlib.use('GTKAgg')
# from matplotlib import rc

# rc('text',usetex=True)
# rc('text.latex', preamble='\usepackage{color}')

from matplotlib.backends.backend_pdf import PdfPages

import matplotlib.pyplot as plt


def usage():
    print 'Usage\t:  ./memorymap.py [...list of trace.out files...]\n'
    print '  Input file is a *.out where each line is formatted as follows:\n\tAddress,Program Counter, [...list of reuse per access...]\n'


def parse_args_return_dirfile_tuples(argv):
    if len(argv) < 2:
       usage()
       exit(1)

    trace_dirfile_list = []
    for arg in argv[1:]:
        arg_tokens = arg.split('/')
        arg_dir = arg_tokens[1]
        arg_filename = arg_tokens[2]
        trace_dirfile_list.append((arg_dir, arg_filename))

    return trace_dirfile_list


def log_time(action):
    sttime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    print "{0} @ {1}".format(action, sttime)


'''
def extract_trace_info(trace_file):
    # 2-bimodal-no-no-partitionedplru.10way-noninclincl-2core.sphinx3.libquantum.txt
    fields          =   trace_file.split( '-' )
    size,pred,l1pref,l2pref,policy_param,inclusion,core_param  =   fields[ 0:7 ]

    if l2pref == 'ip_stride':
        l2pref  =   'pref'
    else :
        l2pref  =   'no pref'

    if policy_param.split('.')[0] == 'plru':
        policy  =   policy_param
    else: 
        policy          =   policy_param.split('.')[ 0 ]
        if policy == 'dbp':
            policy = 'DBP'
        elif 'partitioned' in policy: 
            policy  =   'PLRU'
        size            =   ( ( policy_param.split('.')[ 1 ] ).split( 'way' ) )[ 0 ]

    size            =   int( size )
    cores           =   int( core_param.split( 'core' )[ 0 ] )

    bench0,bench1   =   core_param.split( '.' )[ 1:3 ]

    if inclusion == 'noninclincl' : inclusion = 'inclusive'

    return size, cores, bench0, bench1, l2pref, policy, inclusion
'''


def get_benchmark_names_from_dir_name(dir_name):
    token_list = dir_name.split('_')
    benchmarks = token_list[2:]
    return benchmarks


def extract_trace_info_from_file_name(trace_dir, trace_file):
    benchmark_names = get_benchmark_names_from_dir_name(trace_dir)

    fields = trace_file.split('-')

    # "phase01-core8-bimodal-no-no-plru-8core-cloudsuite-plru.txt"
    phase, core_param, pred, l1pref, l2pref, policy, core_param_again, option, policy_again = fields[0:9]

    phase = phase.replace("phase", "")

    # 4-bimodal-no-no-plru-noninclusive-2core.sphinx3.sphinx3.txt
    # size, pred, l1pref, l2pref, policy, inclusion, core_param = fields[0:7]
    core = core_param.split('core')[1]

    return phase, core, benchmark_names, l1pref, l2pref, policy, "noninclusive"


def parse_trace_files(trace_files):
    # [benchmark][policy][prefetcher][interval][size][inclusion]
    ipc = defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))))
    mpki = defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))))
    lat = defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float)))))))

    IPC = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))))
    MPKI = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))))

    interval = 0
    for trace_dir, trace_file in trace_files:
        phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive = \
            extract_trace_info_from_file_name(trace_dir, trace_file)


        print phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive


        current_ipc = ipc[(bench0, bench1)][policy][pref]
        current_mpki = mpki[(bench0, bench1)][policy][pref]
        current_lat = lat[(bench0, bench1)][policy][pref]

        current_IPC = IPC[(bench0, bench1)][policy][pref]
        current_MPKI = MPKI[(bench0, bench1)][policy][pref]

        with open(trace_file, "r") as f:
            lines = f.readlines()
            for line in range(0, len(lines)):

                # Heartbeat CPU 0 instructions: 100000000 cycles: 291491433 heartbeat IPC: 0.343063 cumulative IPC: 0.343063 heartbeat MPKI: 2.25629 (Simulation time: 0 hr 8 min 45 sec)

                if "Heartbeat" in lines[line]:
                    fields = lines[line].split(' ')
                    core = int(fields[2])
                    interval = int(fields[4])

                    current_ipc[interval][size][inclusion][core] = float(fields[9])
                    current_mpki[interval][size][inclusion][core] = float(fields[15])

                    shift = (interval / 1000000000)  # & ( ( 1 << 41 ) - 1 ) )
                    test = str(interval)
                    Test = map(int, test)
                    tEst = list(reversed(Test))
                    teSt = tEst[0:9]
                    # *** Reached end of trace for Core: N Repeating trace
                    if shift and 0 in teSt and teSt[1:] == teSt[:-1]:
                        latency = float(fields[6])
                        current_lat[size][inclusion][core][interval] = latency

                # CPU 0 cumulative IPC: 1.04882 instructions: 2732707455 cycles: 2605496919
                if lines[line].startswith('CPU') and ('cumulative IPC' in lines[line]):
                    lineparams = lines[line].split(' ')
                    core = int(lineparams[1])
                    Ipc = float(lineparams[4])
                    current_IPC[size][inclusion][core] = Ipc

                if "LLC TOTAL" in lines[line]:
                    misses = float(lines[line].split(':')[3])
                    current_MPKI[size][inclusion][core] = float((misses * 1000) / 1000000000)

            for line in reversed(lines):
                if 'Heartbeat' in line:
                    fields = line.split(' ')
                    core = int(fields[2])
                    if core == 0:
                        interval = int(fields[4])
                        if interval not in current_lat[size][inclusion][core].keys():
                            current_lat[size][inclusion][core][interval] = float(fields[6])
                        break
            for line in reversed(lines):
                if 'Heartbeat' in line:
                    fields = line.split(' ')
                    core = int(fields[2])
                    if core == 1:
                        interval = int(fields[4])
                        if interval not in current_lat[size][inclusion][core].keys():
                            current_lat[size][inclusion][core][interval] = float(fields[6])
                        break

        interval = 0

    return ipc, mpki, IPC, MPKI, lat


# fixme: modify for 4/8 cores
def get_aggr_lat(data, benchmarks, policies, prefetchers, intervals, sizes, inclusion):
    # data0    =   defaultdict( lambda: defaultdict( lambda: defaultdict( lambda: defaultdict( lambda: defaultdict( lambda: defaultdict ( list ) ) ) ) ) )
    data0 = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))))
    data1 = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))))
    for (b0, b1) in benchmarks:
        for p in policies:
            for P in prefetchers:
                for s in sizes:
                    for I in inclusion:
                        # temp    =   0
                        for c in data[(b0, b1)][p][P][s][I].keys():
                            Intervals = data[(b0, b1)][p][P][s][I][c].keys()
                            Intervals.sort()
                            for e, i in enumerate(Intervals):
                                if e == len(Intervals) - 1:
                                    data0[(b0, b1)][p][P][s][I][c] = data[(b0, b1)][p][P][s][I][c][i]
                                data1[(b0, b1)][p][P][s][I][c] = data1[(b0, b1)][p][P][s][I][c] + i

    return data0, data1


def get_sorted_lists(metrics, here):
    benchmarks = []
    policies = []
    prefetchers = []
    intervals = []
    inclusion = []
    sizes = []
    for (b0, b1) in metrics.keys():
        if (b0, b1) not in benchmarks:
            benchmarks.append((b0, b1))
        for p in metrics[(b0, b1)].keys():
            if p not in policies:
                policies.append(p)
            for P in metrics[(b0, b1)][p].keys():
                if P not in prefetchers:
                    prefetchers.append(P)
                for i in metrics[(b0, b1)][p][P].keys():
                    if i not in intervals:
                        intervals.append(i)
                    for s in metrics[(b0, b1)][p][P][i].keys():
                        if not here and p == 'plru': continue
                        if s not in sizes:
                            sizes.append(s)
                        for I in metrics[(b0, b1)][p][P][i][s].keys():
                            if I not in inclusion:
                                inclusion.append(I)

    policies.sort()

    prefetchers.sort()

    intervals.sort()

    sizes.sort()

    inclusion.sort()

    lengthRow = len(benchmarks) * len(policies)
    lengthCol = len(intervals)
    lengthPts = len(sizes)

    return benchmarks, policies, prefetchers, intervals, sizes, inclusion, lengthRow, lengthCol, lengthPts


# fixme: modify for 4/8 cores
def get_data(metrics, benchmarks, policies, prefetchers, intervals, sizes, inclusion):
    data0 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
    data1 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))

    for (b0, b1) in benchmarks:
        for p in policies:
            if p == 'plru': continue
            for P in prefetchers:
                for n, i in enumerate(intervals):
                    if n >= 10: continue
                    for s in sizes:
                        for I in inclusion:
                            data0[(b0, b1)][p][P][I][i].append(metrics[(b0, b1)][p][P][i][s][I][0])
                            data1[(b0, b1)][p][P][I][i].append(metrics[(b0, b1)][p][P][i][s][I][1])
    return data0, data1


# fixme: modify for 4/8 cores
def norm_data(metrics, benchmarks, policies, prefetchers, intervals, sizes, inclusion):
    data0 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    data1 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    for (b0, b1) in benchmarks:
        for p in policies:
            if p == 'plru': continue
            for P in prefetchers:
                for s in sizes:
                    for I in inclusion:
                        data0[(b0, b1)][p][P][I].append(
                            metrics[(b0, b1)][p][P][s][I][0] / metrics[(b0, b1)]['plru']['no pref'][4]['inclusive'][0])
                        data1[(b0, b1)][p][P][I].append(
                            metrics[(b0, b1)][p][P][s][I][1] / metrics[(b0, b1)]['plru']['no pref'][4]['inclusive'][1])
    return data0, data1


# come back here, too
# fixme: modify for 4/8 cores
def get_data2(data, intrvls, benchmarks, policies, prefetchers, intervals, sizes, inclusion):
    data1 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    data2 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    data3 = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    import math
    for (b0, b1) in benchmarks:
        '''
        base0   =   data[(b0,b1)]['plru']['no pref'][4]['inclusive'][0]
        base1   =   data[(b0,b1)]['plru']['no pref'][4]['inclusive'][1]
        baseLat =   ( base0 + base1 ) / 2
        TPbase0 =   intrvls[(b0,b1)]['plru']['no pref'][4]['inclusive'][0] / base0
        TPbase1 =   intrvls[(b0,b1)]['plru']['no pref'][4]['inclusive'][1] / base1
        baseTP  =   pow( ( ( pow( TPbase0, -1 ) + pow( TPbase1, -1 ) ) / 2 ), -1 )
        '''
        # baseTP  =   math.sqrt(TPbase0*TPbase1)
        # baseTP  =   ( TPbase0 + TPbase1 ) / 2
        for p in policies:
            # if p == 'plru': continue
            for P in prefetchers:
                for s in sizes:
                    for I in inclusion:
                        print data[(b0, b1)][p]
                        lat0 = data[(b0, b1)][p][P][s][I][0]
                        lat1 = data[(b0, b1)][p][P][s][I][1]
                        avgLat = (lat0 + lat1) / 2

                        TP0 = intrvls[(b0, b1)][p][P][s][I][0] / lat0
                        TP1 = intrvls[(b0, b1)][p][P][s][I][1] / lat1

                        # harmonic mean
                        avgTP = pow(((pow(TP0, -1) + pow(TP1, -1)) / 2), -1)

                        # geometric mean
                        # avgTP   =   math.sqrt(TP0*TP1)
                        # arithmetic mean
                        # avgTP   =   ( TP0 + TP1 ) / 2

                        normtp = avgTP  # /   baseTP
                        normlat = avgLat  # /   baseLat

                        data1[(b0, b1)][p][P][I].append(normtp)
                        data2[(b0, b1)][p][P][I].append(normlat)
                        data3[(b0, b1)][p][P][I].append(normlat)

    return data3, data1, data2


# fixme: modify for 4/8 cores
def main(argv):
    log_time("starting")
    traces = parse_args_return_dirfile_tuples(argv)
    ipc, mpki, IPC, MPKI, lat = parse_trace_files(traces)

    benchmarks, policies, prefetchers, intervals, sizes, inclusion, lR, lC, lP = get_sorted_lists(ipc, 1)

    # fixme: modify for 4/8 cores
    data0, data1 = get_data(ipc, benchmarks, policies, prefetchers, intervals, sizes, inclusion)
    # fixme: modify for 4/8 cores
    data2, data3 = get_data(mpki, benchmarks, policies, prefetchers, intervals, sizes, inclusion)

    # data4, data5        =   norm_data( IPC, benchmarks, policies, prefetchers, intervals, sizes, inclusion )
    # data6, data7        =   norm_data( MPKI, benchmarks, policies, prefetchers, intervals, sizes, inclusion )

    benchmarks, policies, prefetchers, intervals, sizes, inclusion, lR, lC, lP = get_sorted_lists(ipc, 0)

    # fixme: modify for 4/8 cores
    dataA, dataB = get_aggr_lat(lat, benchmarks, policies, prefetchers, intervals, sizes, inclusion)

    data8, data9, data10 = get_data2(dataA, dataB, benchmarks, policies, prefetchers, intervals, sizes, inclusion)

    benchmarks, policies, prefetchers, intervals, sizes, inclusion, lR, lC, lP = get_sorted_lists(ipc, 1)

    filename = 'data.csv'
    input_file = open(filename, "w")
    input_file.write("policy,benchmark,ipc,mpki\n")

    # benchmarks
    for indexb, (b0, b1) in enumerate(benchmarks):
        # policies
        for indexp, p in enumerate(policies):
            # prefetchers
            for indexP, P in enumerate(prefetchers):
                # interval
                for indexi, i in enumerate(inclusion):
                    for indexs, s in enumerate(sizes):
                        CONFIG = p + "." + i + "." + P + "." + s
                        Ipc = data9[(b0, b1)][p][P][i][0]

                        Mpki = (MPKI[(b0, b1)][p][P][s][i][0] + MPKI[(b0, b1)][p][P][s][i][0]) / 2
                        line = CONFIG + ',' + b0 + ':' + b1 + ',' + str(Ipc) + ',' + str(Mpki) + '\n'

                        input_file.write(line)

    input_file.close()

    log_time("ending")


def parse_and_plot(argv):
    log_time("starting")

    ipcs = []
    mpkis = []
    x_axis_names = []

    traces_dir_files = parse_args_return_dirfile_tuples(argv)

    for trace_dir, trace_file in traces_dir_files:

        phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive = \
            extract_trace_info_from_file_name(trace_dir, trace_file)


        print phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive

        # the result object
        champ_sim_result = ChampSimResult(phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive)

        #Step through file lines
        file_lines = open("./input/{0}/{1}".format(trace_dir, trace_file), 'r').readlines()
        in_region_of_interest = False
        for i, line in enumerate(file_lines):
            if "Region of Interest Statistics" in line:
                in_region_of_interest = True
            if not in_region_of_interest:
                continue
            # We are in region of interest

            if "CPU" in line: # this line is start of data for a new core
                cpu_line = line
                llc_line = file_lines[i + LLC_TOTAL_LINE_POSITION_RELATIVE_TO_CORE]

                # print cpu_line, llc_line
                ipc, n_instructions = extract_ipc_and_instruction_count(cpu_line)
                n_llc_misses = extract_llc_misses(llc_line)

                core = CorePerf(ipc, n_llc_misses, n_instructions)
                champ_sim_result.add_core_result(core)

        # harmonic mean over number of cores
        mean_ipc = champ_sim_result.calculate_harmonic_mean_ipc()
        mean_mpki = champ_sim_result.calculate_harmonic_mean_mpki()
        x_axis_name = "#c:{}, ph:{}\nb:{}".format(champ_sim_result.n_cores, champ_sim_result.phase, champ_sim_result.benchmarks)

        ipcs.append(mean_ipc)
        mpkis.append(mean_mpki)
        x_axis_names.append(x_axis_name)
    print "ipc:", ipcs
    print "mpki:", mpkis
    print "x_axis_name:", x_axis_names
    print "\n"

    barchart(x_axis_names, ipcs, "IPC", "")
    barchart(x_axis_names, mpkis, "MPKI", "")
    barchart_dual_y_shared_x(x_axis_names, "x_label", mpkis, "MPKI", ipcs, "IPCS", "Performance")



if __name__ == "__main__":
    parse_and_plot(sys.argv)
    # barchart(['a', 'b'], [1, 3], "y label", "title")
