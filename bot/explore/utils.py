import numpy as np

def offset_index(data, offset=1):
    """
    Shift the array forward by a specified offset, filling the start with None.
    
    Args:
        data (list or np.ndarray): Input array to offset.
        offset (int): Number of positions to shift forward.
        
    Returns:
        np.ndarray: Offset array with None at the start.
    """
    if offset <= 0:
        return np.array(data)  # No offset, return the original array
    return np.array([data[0]] * offset + list(data[:-offset]))
