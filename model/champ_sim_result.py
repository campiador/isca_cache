# core_eprf.py
# Behnam Heydarshahi, November 2017
# Tufts Computer Architecture Lab
#
# This module models ChampSim performance results for one simulation run
# each simulation has a number of cores

# CONSTANTS

class ChampSimResult:
    def __init__(self, phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive):
        self.phase = phase
        self.n_cores = core
        self.benchmars = benchmark_names
        self.l1pref = l1pref
        self.l2pref = l2pref
        self.policy = policy
        self.is_inclusive = is_inclusive
        self.core_results = []

    def calculate_harmonic_mean_mpki(self):
        pass

    def calculate_harmonic_mean_ipc(self):
        pass

    def get_num_cores(self):
        return self.n_cores

    def add_core_result(self, core_result):
        self.core_results.append(core_result)
