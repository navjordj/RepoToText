import os
import tempfile
from argparse import ArgumentParser
import argparse
from git import Repo
from .tree import create_tree_structure, print_tree
from .prompt_generator import PromptGenerator  # Import the PromptGenerator class


class RepoToText:

    DEFAULT_IGNORE_EXTENSIONS = set(
        [
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".egg-info",
            ".dist-info",
            "__pycache__",
            ".DS_Store",
            ".git",
            ".gitignore",
            ".idea",
            ".vscode",
            ".env",
        ]
    )

    DEFAULT_IGNORE_FOLDERS = set([".git"])


class RepoToText:

    DEFAULT_IGNORE_EXTENSIONS = set(
        [
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".egg-info",
            ".dist-info",
            "__pycache__",
            ".DS_Store",
            ".git",
            ".gitignore",
            ".idea",
            ".vscode",
            ".env",
        ]
    )

    DEFAULT_IGNORE_FOLDERS = set([".git"])

    def __init__(
        self,
        repo_name: str,
        ignore_extensions: list[str] = None,
        ignore_folders: list[str] = None,
        include_folders: list[str] = None,
    ):
        self.repo_name = repo_name
        self.ignore_extensions = RepoToText.DEFAULT_IGNORE_EXTENSIONS.union(
            set(ignore_extensions) if ignore_extensions else []
        )
        self.ignore_folders = RepoToText.DEFAULT_IGNORE_FOLDERS.union(
            set(ignore_folders) if ignore_folders else []
        )
        self.include_folders = set(include_folders) if include_folders else set()

        print(self.ignore_extensions)

    def run(self) -> str:
        base_url = "https://github.com/"
        repo_url = os.path.join(base_url, self.repo_name)
        included_files = []

        with tempfile.TemporaryDirectory(prefix="repo_to_text_") as temp_dir:
            try:
                print(f"Cloning {repo_url}")
                Repo.clone_from(repo_url, temp_dir)
                for root, _, files in os.walk(temp_dir):
                    relative_path = os.path.relpath(root, start=temp_dir)
                    if not self.include_folders or any(
                        relative_path.startswith(folder)
                        for folder in self.include_folders
                    ):
                        for name in files:
                            if not any(
                                name.endswith(ext) for ext in self.ignore_extensions
                            ):
                                file_path = os.path.join(root, name)
                                included_files.append(
                                    os.path.relpath(file_path, start=temp_dir)
                                )
            except Exception as e:
                print(f"An error occurred: {e}")

            tree = create_tree_structure(included_files)
            print_tree(tree)

            # Pass temp_dir as the base_dir argument
            prompt_generator = PromptGenerator(
                included_files, tree, temp_dir, repo_name=self.repo_name
            )
            prompt = prompt_generator.generate_prompt()

        return prompt  # Return the generated prompt


def parse_arguments() -> argparse.Namespace:
    parser = ArgumentParser(description="Repo to Text")
    parser.add_argument("repo_name", help="The name of the repository to clone")
    parser.add_argument(
        "-i",
        "--ignore-extensions",
        nargs="+",
        help="File extensions to ignore (e.g. -i .pyc .git)",
    )
    parser.add_argument(
        "-f",
        "--ignore-folders",
        nargs="+",
        help="Folders to ignore (e.g. -f .git __pycache__)",
    )
    parser.add_argument(
        "-d",
        "--include-folders",
        nargs="+",
        help="Folders to include (e.g. -d src tests)",
    )
    parser.add_argument(
        "-o", "--output-file", dest="output_file", help="Name of output file"
    )
    args = parser.parse_args()

    if args.ignore_folders and args.include_folders:
        parser.error(
            "Both --ignore-folders and --include-folders can't be set at the same time."
        )

    return args


def main() -> None:
    args = parse_arguments()
    repo_to_text = RepoToText(
        args.repo_name,
        args.ignore_extensions,
        args.ignore_folders,
        args.include_folders,
    )
    prompt = repo_to_text.run()  # Get the generated prompt

    if args.output_file:  # Check if the output file argument is provided
        with open(
            args.output_file, "w", encoding="utf-8"
        ) as file:  # Open the output file in write mode with utf-8 encoding
            file.write(prompt)  # Write the prompt to the file
        print(f"Prompt written to {args.output_file}")
    else:
        print(prompt)  # Print the prompt if no output file is specified


if __name__ == "__main__":
    main()
