import subprocess


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
