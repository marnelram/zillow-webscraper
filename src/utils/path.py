import os


def print_file_tree(directory):
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, "").count(os.sep)
        indent = " " * 4 * (level)
        print(f"{indent}[{os.path.basename(root)}/]")
        sub_indent = " " * 4 * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")


# Example usage
project_directory = "C:/python-projects/zillow_webscraper/"
print_file_tree(project_directory)
