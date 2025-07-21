# Welcome to SORBA SDE Python Editor, programming in python language integrated with SORBA.
# Use sde["ASSET.GROUP.TAG"] to read or write SDE tags or sde[ASSET+".GROUP.TAG"] for generic code
# based on Asset property.
# Declare as global for sharing imported modules, functions or variables between scripts.
# Use debug(args) or debug_sde (sde_tags_names) to log in the debug.log file with timestamp.
# Look for built-in SDE scripts functions and other SDE python modules like timer, counter, OEE for easy
# For importing custom modules from any path add in OnStart script: import sys; sys.path.append('new path')
# scripting.
# Enter your python code here.
def sum_two_numbers(a, b):
    return a + b

# Example usage
import random
my_random_integer = random.randint(1, 100)  # generates a random integer between 1 and 100

number1 = my_random_integer
number2 = my_random_integer
result = sum_two_numbers(number1, number2)
debug(f"The sum of {number1} and {number2} is {result}")