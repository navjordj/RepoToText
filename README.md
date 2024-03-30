# RepoToText

RepoToText is a Python library designed to convert codebases into a single text file. This can be particularly useful for long context Language Models (LLMs) such as Gemini 1.5 Pro, allowing them to process entire repositories as a single continuous text stream.

## Features

- Clone GitHub repositories and convert them to a single text representation.
- Configurable to ignore specific file extensions and directories.
- Option to include specific folders for a focused dataset.
- Simple CLI interface for easy use.

## Installation

Before you can use RepoToText, you need to have Python installed on your system (Python 3.6 or newer is recommended). You can then install RepoToText using pip:

```sh
pip install git+https://github.com/yourusername/RepoToText.git
```
## Usage
RepoToText can be used both as a standalone command-line (CLI) tool and as a library within other Python scripts.

### As a CLI Tool
To use RepoToText from the command line, simply invoke it with the repository you wish to convert:
```sh
repo_to_text <GitHub_Repo_URL> -o <output_filename.txt>
```

You can also ignore specific file extensions and directories or include specific folders:

```sh
repo_to_text <GitHub_Repo_URL> -i .pyc .git -d src tests -o <output_filename.txt>
```

Example using this repository
```sh
repo_to_text navjordj/repo_to_text -o prompts/repo_to_text_prompt.md
```

### Using a Local Directory

To process a local directory instead of a GitHub repository, use the -t option to specify local:

```sh
repo_to_text /path/to/local/directory -t local -o <output_filename.md>
```

### As a Library
RepoToText can also be imported into your Python scripts for more customized usage:

```python
from repo_to_text import RepoToText

# For a GitHub repository
repo_to_text = RepoToText(
    source='username/repository',
    ignore_extensions=['.pyc', '.git'],
    include_folders=['src', 'tests']
)

text_output = repo_to_text.run()

# For a local directory
repo_to_text_local = RepoToText(
    source='/path/to/local/directory',
    source_type='local',
    ignore_extensions=['.pyc', '.git'],
    include_folders=['src', 'tests']
)

text_output_local = repo_to_text_local.run()
```