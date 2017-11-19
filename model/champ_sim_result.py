# core_eprf.py
# Behnam Heydarshahi, November 2017
# Tufts Computer Architecture Lab
#
# This module models ChampSim performance results for one simulation run
# each simulation has a number of cores

from scipy import stats


class ChampSimResult:
    def __init__(self, phase, core, benchmark_names, l1pref, l2pref, policy, is_inclusive):
        self.phase = phase
        self.n_cores = core
        self.benchmarks = benchmark_names
        self.l1pref = l1pref
        self.l2pref = l2pref
        self.policy = policy
        self.is_inclusive = is_inclusive
        self.core_results = []

    def calculate_harmonic_mean_mpki(self):
        mpki_list = [core_result.llc_mpki for core_result in self.core_results]
        mpki_list = map(float, mpki_list)
        mpki_harmonic_mean = stats.hmean(mpki_list)
        return mpki_harmonic_mean

    def calculate_harmonic_mean_ipc(self):
        ipc_list = [core_result.ipc for core_result in self.core_results]
        ipc_list = map(float, ipc_list)
        ipc_harmonic_mean = stats.hmean(ipc_list)

        return ipc_harmonic_mean

    def get_num_cores(self):
        return self.n_cores

    def add_core_result(self, core_result):
        self.core_results.append(core_result)

    def set_core_hitrates(self, core_index, core_hitrates):
        core_index = int(core_index)
        self.core_results[core_index].set_hitrates(core_hitrates)
