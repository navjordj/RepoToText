import os
from typing import Dict, Optional
from string import Template


class PromptGenerator:
    def __init__(
        self, file_paths: list[str], tree: dict, base_dir: str, repo_name: str
    ):
        self.file_paths = file_paths
        self.tree = tree
        self.base_dir = base_dir
        self.repo_name = repo_name

    def generate_prompt(self) -> str:
        tree_str = self._generate_tree_str(self.tree)
        file_contents = self._generate_file_contents()

        main_template = Template(
            """
# Structure of repository $repo_name

## Tree Structure
$tree

## Files

$file_contents
"""
        )

        # Substitute the placeholders with the actual tree structure and file contents
        prompt = main_template.substitute(
            tree=tree_str, file_contents=file_contents, repo_name=self.repo_name
        )
        return prompt

    def _generate_tree_str(
        self, tree: Dict[str, Optional[dict]], indent: str = ""
    ) -> str:
        tree_str = ""
        for key, value in tree.items():
            if value:
                tree_str += f"{indent}├── {key}\n"
                tree_str += self._generate_tree_str(value, indent + "│   ")
            else:  # File
                tree_str += f"{indent}├── {key}\n"
        return tree_str

    def _generate_file_contents(self) -> str:
        file_contents = ""

        file_template = Template(
            """
### File Name: $file_name
### File Path: $file_path

### File contents
$content


            """
        )
        for relative_path in self.file_paths:
            try:
                file_path = os.path.join(self.base_dir, relative_path)
                with open(file_path, "r") as file:
                    content = file.read()
                    # Strip the base_dir from the file_path
                    display_path = os.path.relpath(file_path, start=self.base_dir)

                    file_contents += file_template.substitute(
                        file_name=os.path.basename(relative_path),
                        file_path=display_path,
                        content=content,
                    )
            except Exception as e:
                file_contents += f"Error reading {relative_path}: {e}\n\n"
        return file_contents
