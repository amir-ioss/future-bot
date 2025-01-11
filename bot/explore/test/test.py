import numpy as np
import json
import os

# Clear console for Windows or Unix-based systems
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


with open('data.json', 'r') as file:
    functions = json.load(file)

def input(type):
    rand_arr = np.random.randint(2000, 2100, size=4)
    rand_int = np.random.randint(1, 11)  
    rand_flo = np.random.random()  

    if type == "tuple of integers":
        return (2, 2)
    elif type == "numpy array":
        return rand_arr
    elif type == "number" or type == "integer" or type == "element":
        return rand_int
    elif type == "float":
        return rand_flo
    elif type == "string":
        return ''.join(np.random.choice(np.array(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")), 10))
    elif type == "list or iterable": 
        return np.fromiter(rand_arr, dtype=int, count=2)
    return


# Define color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"  # Reset color to default
testArea = 1

def test_functions():
    func_list = functions.items()
    win = 0
    for idx, (func_name, func_data) in enumerate(func_list):
        if func_name == "binary_search": continue
        if func_name in ["array", "fromiter","where","last", "lastindexof"]: continue # need special func

        if func_name == "mode": continue
        if func_name in ["new_color", "new_label", "new_label", "new_label" , "new_table", "new_box", "new_line", "new_linefill"]: continue # PLOT
        if func_name == "percentrank" or func_name == "percentile_nearest_rank": continue #percentile_nearest_rank
      

        if func_name == "standardize": continue # (arr - np.mean(arr)) / np.std(arr)

        # if idx < testArea or idx > testArea+10: continue 

        inputs = {}
        # inputs = []
        for param in func_data["Inputs"]:
            name = param["name"]
            type = param["type"]
            inputs[name] = input(type)
            # inputs.append(input(type))

        # Dynamically construct the function call
            params = ', '.join([f"inputs['{i}']" for i in inputs])  
            out = ', '.join([i['type'] for i in func_data["Outputs"]])
        try:
            if func_name == "slice": result = inputs['array'][1:4]
            elif func_name == "cov": 
                result = np.cov([inputs['array'], inputs['array']])
            elif func_name == "join":
                result = inputs['delimiter'].join(map(str, inputs['array']))
            elif func_name == "shift": result = np.roll(inputs['array'], -1)[-1] = np.nan

            elif func_name in ["new_float", "new_int", "new_string"]: result = inputs['array'] * inputs['count']
            elif func_name == "reverse": result = inputs['array'][::-1]
            elif func_name == "set": result = inputs['array'][inputs['index']] = inputs['value']



            else: result = eval(f"np.{func_name}({params})")
            
            # print(f"----------- {func_name} ------------\nnp.{func_name}({params})\n{GREEN}{out} :: {result}{RESET}\n")
            
            win += 1
        except Exception as e:
            print(f"{RED}----------- {func_name} ({func_data['Name']}) ------------\n{inputs}\nnp.{func_name}({params})\n{e}{RESET}\n")

    print(win, "/", len(func_list))

if __name__ == "__main__":
    # print(functions)
    clear_console() 
    test_functions()

    result = eval(f"np.abs([0.82487371, 0.74264397])")
