# !/usr/sup/bin/python
# post_process_champsim_results.py
# Behnam Heydarshahi, November 2017
# Tufts Computer Architecture Lab
#
# This program reads ChampSim output files and plots them (llc_mpki and ipc)

from graphics.plot import barchart_dual_y_shared_x, plot_x_y_line, plot_two_sided_x_y_lines_withsubplots
from graphics.subplotable import SubPlotable
from model.champ_sim_result import ChampSimResult
from model.core_perf import LLC_TOTAL_LINE_POSITION_RELATIVE_TO_CORE, extract_ipc_and_instruction_count, \
    extract_llc_misses, CorePerf

import sys
import datetime

def usage():
    print 'Usage\t:  ./memorymap.py [...list of trace.out files...]\n'
    print 'Input file is a *.out where each line is formatted as follows:\n' \
          '\tAddress,Program Counter, [...list of reuse per access...]\n'


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


def extract_core_number_and_hitrates(ccc_line):
    line_tokens = ccc_line.split(":")
    core_tokens = line_tokens[0].split()

    core_number = core_tokens[1]

    core_hitrates= line_tokens[1:-2]

    return core_number, core_hitrates


def parse_and_plot(argv):
    log_time("starting")

    mean_ipcs = []
    mean_mpkis = []
    x_axis_names = []

    traces_dir_files = parse_args_return_dirfile_tuples(argv)

    champsim_results = []

    for trace_dir, trace_file in traces_dir_files:
        ccc_subplotables = []


        phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive = \
            extract_trace_info_from_file_name(trace_dir, trace_file)


        print phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive

        # the result object
        champsim_result = ChampSimResult(phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive)

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
                champsim_result.add_core_result(core)

            if "CACHE CAPACIITY CURVE (Hit Rate)" in line:  
                #  e.g. line  = CORE 0 CACHE CAPACIITY CURVE (Hit Rate):0.272091:0.466812:0.631125:0.675701:0.740989:0:
                ccc_line = line
                core_number, core_hitrates = extract_core_number_and_hitrates(ccc_line)
                champsim_result.set_core_hitrates(core_number, core_hitrates)

        # harmonic mean over number of cores
        mean_ipc = champsim_result.calculate_harmonic_mean_ipc()
        mean_mpki = champsim_result.calculate_harmonic_mean_mpki()
        x_axis_name = "#c:{}, ph:{}\nb:{}".format(champsim_result.n_cores, champsim_result.phase,
                                                  [b[0:4] for b in champsim_result.benchmarks]) # first four chars of b

        mean_ipcs.append(mean_ipc)
        mean_mpkis.append(mean_mpki)
        x_axis_names.append(x_axis_name)

        champsim_results.append(champsim_result)


    # = [[benchmark0_core0, behcnmark0_core1, ... ], ... []]
    all_benchmarks_cores_ipcs =  []
    all_benchmarks_cores_mpkis =  []

    for champsim_result in champsim_results:  # each champsim_result represents one benchmark
        one_benchmark_cores_ipcs = []
        one_benchmark_cores_mpkis = []
        for core_result in champsim_result.core_results:
            one_benchmark_cores_ipcs.append(core_result.ipc)
            one_benchmark_cores_mpkis.append(core_result.llc_mpki)
        all_benchmarks_cores_ipcs.append(one_benchmark_cores_ipcs)
        all_benchmarks_cores_mpkis.append(one_benchmark_cores_mpkis)

    print "all benchmark ipcs:", all_benchmarks_cores_ipcs
    print "all benchmarks mpkis", all_benchmarks_cores_mpkis



        # # CCC plots for a benchmark
        # for i, core in enumerate(champ_sim_result.core_results):
        #     print "core hitrates:", core.core_capacity_hitrates
        #     ccc_subplotable = SubPlotable("Core {}".format(i), [1, 2, 4, 8, 16], core.core_capacity_hitrates,
        #                                   [0 for _ in core.core_capacity_hitrates])
        #     ccc_subplotables.append(ccc_subplotable)
        # # plot_x_y_line("Cache Capacity Curve for benchmark {}".format(champ_sim_result.benchmarks),
        # #               "Ways", "CCC hit-rate", ccc_subplotables, "ccc")

    print "mean ipcs:", mean_ipcs
    print "mean mpkis:", mean_mpkis
    print "x_axis_name:", x_axis_names
    print "\n"

    x_values = [4, 8, 16, 32]


    mean_ipcs_subplotable = SubPlotable("IPC", x_values, mean_ipcs, [0 for _ in mean_ipcs])
    mean_mpkis_subplotable = SubPlotable("MPKI", x_values, mean_mpkis, [0 for _ in mean_mpkis])



    # barchart(x_axis_names, ipcs, "IPC", "")
    # barchart(x_axis_names, mpkis, "MPKI", "")
    plot_two_sided_x_y_lines_withsubplots("CloudSuite Curves", "LLC Size (MB)", "IPC", "MPKI",
                                          [mean_ipcs_subplotable, mean_mpkis_subplotable], "llc_size_sweep")

if __name__ == "__main__":
    parse_and_plot(sys.argv)
