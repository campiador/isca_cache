# core_eprf.py
# Behnam Heydarshahi, November 2017
# Tufts Computer Architecture Lab
#
# This module models ChampSim performance results for one core

from __future__ import division

LLC_TOTAL_LINE_POSITION_RELATIVE_TO_CORE = 19


class CorePerf:
    def __init__(self, ipc, llc_misses, n_instructions):
        self.ipc = ipc
        self.llc_misses = llc_misses
        self.n_instructions = n_instructions
        self.llc_mpki = calculate_core_mpki(llc_misses, n_instructions)
        self.core_capacity_hitrates = []  # for 1, 2, 4, 8, 16

    def set_hitrates(self, hitrates):
        self.core_capacity_hitrates = hitrates


# static module methods
def extract_ipc_and_instruction_count(cpu_line):
    line_tokens = cpu_line.split()
    ipc = line_tokens[4]
    n_instructions = line_tokens[6]
    return ipc, n_instructions


def extract_llc_misses(llc_line):
    line_tokens = llc_line.split()
    n_misses = line_tokens[7]
    return n_misses


def calculate_core_mpki(misses, n_instructions):
    return (int(misses) * 1000) / int(n_instructions)
