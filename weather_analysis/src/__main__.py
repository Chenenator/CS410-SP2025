import os

# Method 1: Using os.path to get the root directory

parent_dir = os.path.dirname(os.getcwd()) + "/data/bostonweather.csv"
print(f"Root directory (using os.path): {parent_dir}")
