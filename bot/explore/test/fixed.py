import numpy as np
from scipy.stats import mode


# Calculate the mode
result = mode(inputs['array'])

# Get the last index of the value
def last_index_of(arr, value):
    indices = np.where(arr == value)[0]  # Find all matching indices
    return indices[-1] if indices.size > 0 else -1  # Return last index or -1 if not found

inputs = {'array': np.array([2095, 2038, 2066, 2033, 2038])}



def percentile_nearest_rank(arr, percentile):
    # Sort the array using numpy
    sorted_arr = np.sort(arr)
    N = len(sorted_arr)
    
    # Calculate the rank (index) for the given percentile
    rank = int(np.floor((percentile / 100) * (N - 1)))
    
    # Return the value at the calculated rank
    return sorted_arr[rank]

# Example usage
data = np.array([2002, 2069, 2041, 2084])
percentile = 50  # Median (50th percentile)

result = percentile_nearest_rank(data, percentile)

