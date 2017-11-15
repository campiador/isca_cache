# core_eprf.py
# Behnam Heydarshahi, November 2017
# Tufts Computer Architecture Lab
#
# This module models ChampSim performance results for one core

LLC_TOTAL_LINE_POSITION_RELATIVE_TO_CORE = 19


class CorePerf:
    def __init__(self, ipc, llc_misses, n_instructions):
        self.ipc = ipc
        self.llc_misses = llc_misses
        self.n_instructions = n_instructions
        self.llc_mpki = self.llc_misses / self.n_instructions
