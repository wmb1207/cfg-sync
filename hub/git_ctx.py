


import git
from git.exc import NoSuchPathError
from valhalla.config import Config


class GitCtx:
    cfg: Config
    repo: git.Repo

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def __enter__(self):
        try:
            self.repo = git.Repo(self.cfg.repositoy_path)
        except NoSuchPathError:
            self.repo = git.Repo.clone_from(
                self.cfg.repository, self.cfg.repositoy_path
            )

        return self.repo

    def __exit__(self, exc_type, exc_value, traceback):
        _ = (exc_type, exc_value, traceback)
        
        del self.repo
        return False
