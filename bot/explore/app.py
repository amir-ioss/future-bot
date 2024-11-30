import numpy as np
import talib

# Generate random data
close = np.random.random(100)

inputs = {
    "0": "talib.EMA(close,15)",
    "1": "talib.SMA(close,10)",
    "2": "talib.MA(close,5)",
    "3": "[output['0'][i] == output['1'][i] for i in range(len(close)) if output['0'][i] is not None]",
    "4": "[output['3'][i] < output['2'][i] for i in range(len(close)) if output['3'][i] is not None]"
}
# # Inputs containing steps and conditions
# inputs = {
#     "1": "talib.SMA(close, 5)",  # Simple Moving Average
#     "2": "talib.EMA(close, 5)",  # Exponential Moving Average
#     "3": "[x > output['1'][i] for i, x in enumerate(close)]",  # Close greater than SMA
#     "4": "[output['3'][i] > output['2'][i] for i in range(len(close)) if output['3'][i] is not None]", 
#     "5": "talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)[0]",  # MACD line
#     "6": "[output['5'][i] > output['4'][i] for i in range(len(close)) if output['4'][i] is not None]", 
# }
# # Initialize the output dictionary
output = {}
# Function to resolve dependencies dynamically
def resolve_dependencies(inputs):
    # print()
    # for key, formula in list(inputs.items()):
    #     print(key)
    # return
    # Keep processing until all inputs are resolved
    while inputs:
        for key, formula in list(inputs.items()):
            print(key, formula)
            try:
                # Attempt to evaluate the formula
                output[key] = eval(formula)
                del inputs[key]  # Remove resolved item
            except KeyError:
                # Skip if dependencies are not resolved yet
                pass

# Resolve all inputs
resolve_dependencies(inputs)

# Print the final output
print("---", output)