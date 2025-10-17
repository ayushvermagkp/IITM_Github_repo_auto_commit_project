import os
from github import Github, GithubException
import base64

class GitHubClient:
    def __init__(self, token=None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.g = Github(self.token)
        self.user = self.g.get_user()
    
    def create_repository(self, name, description="", private=False):
        """Create a new GitHub repository"""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False
            )
            return repo
        except GithubException as e:
            print(f"Error creating repository: {e}")
            return None
    
    def enable_pages(self, repo, branch="main", path="/"):
        """Enable GitHub Pages for the repository"""
        try:
            page = repo.create_page(
                source={
                    "branch": branch,
                    "path": path
                }
            )
            return page
        except GithubException as e:
            print(f"Error enabling pages: {e}")
            return None
    
    def commit_files(self, repo, files, commit_message="Initial commit"):
        """Commit multiple files to the repository"""
        try:
            for file_path, content in files.items():
                repo.create_file(file_path, commit_message, content)
            return repo.get_branch("main").commit.sha
        except GithubException as e:
            print(f"Error committing files: {e}")
            return None
