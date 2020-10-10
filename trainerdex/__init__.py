import subprocess

commit_count = (
    subprocess.run(["git", "rev-list", "HEAD", "--count"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)
commit_sha = (
    subprocess.run(["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)


__version__ = "0.{commit_count}-{commit_sha}".format(
    commit_count=commit_count, commit_sha=commit_sha
)
VERSION = __version__
