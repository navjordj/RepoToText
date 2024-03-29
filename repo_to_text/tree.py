from collections import defaultdict
import os

def create_tree_structure(included_files: list[str]) -> dict:
    tree = defaultdict(dict)
    for file_path in included_files:
        parts = file_path.split(os.sep)
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = None
    return tree

def print_tree(tree: dict, indent: str = "") -> None:
    for key, value in tree.items():
        if value:
            print(f"{indent}├── {key}")
            print_tree(value, indent + "│   ")
        else:
            print(f"{indent}├── {key}")
