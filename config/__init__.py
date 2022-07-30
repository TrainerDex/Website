import git


def get_version():
    repo = git.Repo(search_parent_directories=True)
    count = len(list(repo.iter_commits()))
    return f"0.{count} ({repo.head.commit.hexsha[:7]})"


__version__ = get_version()
