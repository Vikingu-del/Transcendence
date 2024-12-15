def example_function(arg1, arg2, arg3):
    print(f"{arg1}, {arg2}, {arg3}")

# Dictionary containing the arguments
data = {'arg1': {'arg1.0': {'arg1.1': 'value1.1'}}, 'arg2': 'value2', 'arg3': 'value3'}

# Unpacking the dictionary into keyword arguments
example_function(**data)