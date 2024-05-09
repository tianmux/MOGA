
import numpy as np

def locate_subarray(two_d_array, target):
    for i, sub_array in enumerate(two_d_array):
        if np.array_equal(sub_array, target):
            return i  # Return the index of the sub-array
    return -1  # Return -1 if the target is not found
