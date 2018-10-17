import math

import numpy as np


def drop_zeros(a_list):
    return [i for i in a_list if i > 0]


def log_binning(counter_dict, bin_count=35):
    keys = counter_dict.keys()
    values = counter_dict.values()

    max_x = math.log10(max(keys))
    max_y = math.log10(max(values))
    max_base = max([max_x, max_y])

    min_x = math.log10(min(drop_zeros(keys)))

    bins = np.logspace(min_x, max_base, num=bin_count)

    bin_means_y = (np.histogram(list(keys), bins, weights=list(values))[0] /
                   np.histogram(list(keys), bins)[0])
    bin_means_x = (np.histogram(list(keys), bins, weights=list(keys))[0] /
                   np.histogram(list(keys), bins)[0])

    return bin_means_x, bin_means_y
