from setuptools import setup, find_packages

setup(
    name="repo_to_text",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gitpython",
    ],
    entry_points={
        "console_scripts": [
            "repo_to_text = repo_to_text.main:main",
            "rtt = repo_to_text.main:main",
        ],
    },
    description="A library for cloning GitHub repositories and printing the contents of the repository to the console.",
)
