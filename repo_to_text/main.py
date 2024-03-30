import os
import tempfile
from argparse import ArgumentParser
import argparse
from git import Repo
from .tree import create_tree_structure, print_tree
from .prompt_generator import PromptGenerator
import fnmatch


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
            ".egg-info",
        ]
    )

    DEFAULT_IGNORE_FOLDERS = set([".git", "*.egg-info"])

    def __init__(
        self,
        repo_name: str = None,
        local_dir: str = None,
        ignore_extensions: list[str] = None,
        ignore_folders: list[str] = None,
        include_folders: list[str] = None,
    ):
        if not repo_name and not local_dir:
            raise ValueError("Either repo_name or local_dir must be provided.")
        self.repo_name = repo_name
        self.local_dir = local_dir
        self.ignore_extensions = self.DEFAULT_IGNORE_EXTENSIONS.union(
            ignore_extensions or []
        )
        self.ignore_folders = self.DEFAULT_IGNORE_FOLDERS.union(ignore_folders or [])
        self.include_folders = set(include_folders or [])

        print(self.ignore_extensions, self.ignore_folders)

    def run(self) -> str:
        included_files = []

        if self.repo_name:
            base_url = "https://github.com/"
            repo_url = os.path.join(base_url, self.repo_name)
            with tempfile.TemporaryDirectory(prefix="repo_to_text_") as temp_dir:
                try:
                    print(f"Cloning {repo_url}")
                    Repo.clone_from(repo_url, temp_dir)
                    base_dir = temp_dir
                except Exception as e:
                    print(f"An error occurred during cloning: {e}")
                    return ""
        elif self.local_dir:
            print(f"Using local directory: {self.local_dir}")
            base_dir = self.local_dir
        else:
            raise ValueError("No source provided.")

        try:
            for root, dirs, files in os.walk(base_dir):
                relative_path_parts = os.path.relpath(root, start=base_dir).split(
                    os.sep
                )

                # Debugging print for current directory being processed
                print(f"Processing directory: {root}")

                if any(
                    any(
                        fnmatch.fnmatch(part, pattern)
                        for pattern in self.ignore_folders
                    )
                    for part in relative_path_parts
                ):
                    print(
                        f"Skipping directory due to ignore_folders match: {root}"
                    )  # Debugging print
                    continue

                if self.include_folders and not any(
                    any(
                        fnmatch.fnmatch(part, pattern)
                        for pattern in self.include_folders
                    )
                    for part in relative_path_parts
                ):
                    print(
                        f"Skipping directory due to no include_folders match: {root}"
                    )  # Debugging print
                    continue

                for name in files:
                    if any(name.endswith(ext) for ext in self.ignore_extensions):
                        print(
                            f"Skipping file due to ignore_extensions match: {name}"
                        )  # Debugging print
                        continue

                    file_path = os.path.join(root, name)
                    relative_file_path = os.path.relpath(file_path, start=base_dir)
                    included_files.append(relative_file_path)

                    # Debugging print for file being included
                    print(f"Including file: {relative_file_path}")

        except Exception as e:
            print(f"An error occurred during file processing: {e}")
            return ""

        tree = create_tree_structure(included_files)
        print_tree(tree)

        # Pass base_dir as the base_dir argument
        prompt_generator = PromptGenerator(
            included_files, tree, base_dir, repo_name=self.repo_name or self.local_dir
        )
        prompt = prompt_generator.generate_prompt()

        return prompt  # Return the generated prompt


def parse_arguments() -> argparse.Namespace:
    parser = ArgumentParser(description="Repo to Text")
    parser.add_argument("-r", "--repo-name", help="The name of the repository to clone")
    parser.add_argument(
        "-l", "--local-dir", help="Path to a local directory to analyze"
    )
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

    if not args.repo_name and not args.local_dir:
        parser.error("Either --repo-name or --local-dir must be provided.")

    return args


def main() -> None:
    args = parse_arguments()
    repo_to_text = RepoToText(
        repo_name=args.repo_name,
        local_dir=args.local_dir,
        ignore_extensions=args.ignore_extensions,
        ignore_folders=args.ignore_folders,
        include_folders=args.include_folders,
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
