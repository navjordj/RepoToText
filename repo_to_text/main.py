import os
import tempfile
from argparse import ArgumentParser
import argparse
from git import Repo


# Assuming these are correctly implemented elsewhere
from .tree import create_tree_structure, print_tree
from .prompt_generator import PromptGenerator


class RepoToText:
    DEFAULT_IGNORE_EXTENSIONS = {
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
    }
    DEFAULT_IGNORE_FOLDERS = {".git"}

    def __init__(
        self,
        source: str,
        source_type: str = "remote",  # 'remote' or 'local'
        ignore_extensions: list[str] = None,
        ignore_folders: list[str] = None,
        include_folders: list[str] = None,
    ):
        self.source = source
        self.source_type = source_type
        self.ignore_extensions = self.DEFAULT_IGNORE_EXTENSIONS.union(
            ignore_extensions or []
        )
        self.ignore_folders = self.DEFAULT_IGNORE_FOLDERS.union(ignore_folders or [])
        self.include_folders = set(include_folders or [])

    def run(self) -> str:
        included_files = []

        if self.source_type == "remote":
            repo_url = f"https://github.com/{self.source}"
            with tempfile.TemporaryDirectory(prefix="repo_to_text_") as temp_dir:
                self._clone_repo(repo_url, temp_dir)
                included_files = self._collect_included_files(temp_dir)
        elif self.source_type == "local":
            included_files = self._collect_included_files(self.source)

        tree = create_tree_structure(included_files)
        print_tree(tree)

        prompt_generator = PromptGenerator(
            included_files, tree, self.source, repo_name=self.source
        )
        prompt = prompt_generator.generate_prompt()

        return prompt

    def _clone_repo(self, repo_url: str, temp_dir: str):
        try:
            print(f"Cloning {repo_url}")
            Repo.clone_from(repo_url, temp_dir)
        except Exception as e:
            print(f"An error occurred while cloning the repo: {e}")

    def _collect_included_files(self, temp_dir: str) -> list:
        included_files = []
        for root, dirs, files in os.walk(temp_dir, topdown=True):
            dirs[:] = [
                d for d in dirs if not self._should_ignore_folder(os.path.join(root, d))
            ]
            relative_path = os.path.relpath(root, start=temp_dir)
            if not self.include_folders or self._is_included_folder(relative_path):
                for name in files:
                    if not self._should_ignore_file(name):
                        file_path = os.path.join(root, name)
                        included_files.append(
                            os.path.relpath(file_path, start=temp_dir)
                        )
        return included_files

    def _should_ignore_folder(self, path: str) -> bool:
        folder_name = os.path.basename(path)
        return folder_name in self.ignore_folders

    def _is_included_folder(self, relative_path: str) -> bool:
        return any(folder in relative_path for folder in self.include_folders)

    def _should_ignore_file(self, filename: str) -> bool:
        return any(filename.endswith(ext) for ext in self.ignore_extensions)


def parse_arguments() -> argparse.Namespace:
    parser = ArgumentParser(description="Repo to Text")
    parser.add_argument(
        "source",
        help="The name of the repository to clone or the path to a local directory",
    )
    parser.add_argument(
        "-t",
        "--source-type",
        choices=["remote", "local"],
        default="remote",
        help="Specify 'remote' for a GitHub repository or 'local' for a local directory",
    )
    parser.add_argument(
        "-i", "--ignore-extensions", nargs="+", help="File extensions to ignore"
    )
    parser.add_argument("-f", "--ignore-folders", nargs="+", help="Folders to ignore")
    parser.add_argument("-d", "--include_folders", nargs="+", help="Folders to include")
    parser.add_argument(
        "-o", "--output-file", dest="output_file", help="Name of the output file"
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
        args.source,
        args.source_type,
        args.ignore_extensions,
        args.ignore_folders,
        args.include_folders,
    )
    prompt = repo_to_text.run()

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as file:
            file.write(prompt)
        print(f"Prompt written to {args.output_file}")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
