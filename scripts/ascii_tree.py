import os

def print_tree(directory, indent="", prefix=""):
    # Print the current directory or file
    print(prefix + os.path.basename(directory))
    # If it's a directory, list its contents
    if os.path.isdir(directory):
        # Get all entries in the directory
        entries = sorted(os.listdir(directory))
        for i, entry in enumerate(entries):
            path = os.path.join(directory, entry)
            # Determine if this is the last entry
            is_last = i == len(entries) - 1
            # Set the prefix for the next level
            new_prefix = indent + ("└── " if is_last else "├── ")
            # Set the indent for the next level
            new_indent = indent + ("    " if is_last else "│   ")
            print_tree(path, new_indent, new_prefix)

# Replace '.' with your directory path if needed
print_tree('.')