
import logging
import os
import rumps
import git
from git.exc import NoSuchPathError

from dataclasses import dataclass

class NoRepoCloned(Exception): ...

@dataclass
class Config:
    repository: str
    repositoy_path: str



def pull(cfg: Config):
    repo: git.Repo
    try:
        repo = git.Repo(cfg.repositoy_path)
    except NoSuchPathError:
        repo = git.Repo.clone_from(cfg.repository, cfg.repositoy_path)
    repo.remote().pull()

def push(cfg: Config):
    try:
        repo: git.Repo = git.Repo(cfg.repositoy_path)
    except NoSuchPathError:
        logging.error(f"No repo cloned under {cfg.repositoy_path}")
        raise NoRepoCloned from NoSuchPathError

    repo.index.diff(repo.head.commit)
    


class App(rumps.App):

    cfgs: Config | None
    
    def with_cfgs(self, cfgs: Config):
        self.cfgs = cfgs
    
    
    @rumps.clicked("Push configs")
    def push_cfgs(self, _):
        print("this is configuring")
        rumps.notification("wmb-cfgs", "time to check this shit", "hi!!1")


def main():
    App("wmb-configs").run()



