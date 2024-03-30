import unittest
import os
from repo_to_text import (
    RepoToText,
)  # Adjust the import path as necessary


class TestRepoToTextFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(__file__)  # Gets the directory of the current script
        cls.test_repo_dir = os.path.join(base_dir, "example_repo")

    def test_ignoring_extensions(self):
        # Test ignoring specific file extensions (.pyc)
        repo_to_text = RepoToText(
            source=self.test_repo_dir,
            source_type="local",
            ignore_extensions=[".pyc"],
        )
        included_files = repo_to_text._collect_included_files(self.test_repo_dir)

        # Verify that files with .pyc extension are not included
        self.assertTrue(
            all(".pyc" not in file for file in included_files),
            "Files with .pyc extension were not ignored as expected.",
        )

    def test_ignoring_folders(self):
        # Test ignoring specific folders ('to_be_ignored_folder')
        repo_to_text = RepoToText(
            source=self.test_repo_dir,
            source_type="local",
            ignore_folders=["to_be_ignored_folder"],
        )
        included_files = repo_to_text._collect_included_files(self.test_repo_dir)

        # Verify that files within 'to_be_ignored_folder' are not included
        self.assertTrue(
            all("to_be_ignored_folder" not in file for file in included_files),
            "Files within 'to_be_ignored_folder' were not ignored as expected.",
        )

    def test_including_files(self):
        repo_to_text = RepoToText(
            source=self.test_repo_dir,
            source_type="local",
            ignore_folders=["to_be_ignored_folder"],
        )
        included_files = repo_to_text._collect_included_files(self.test_repo_dir)

        self.assertEqual(2, len(included_files))


if __name__ == "__main__":
    unittest.main()
