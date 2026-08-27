import subprocess


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def init_repo(path, branch="main"):
    """git init with a committer identity so commits work on bare CI runners."""
    git(path, "init", "-q", "-b", branch)
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "test")
