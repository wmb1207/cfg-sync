from datetime import datetime
import logging
import os
import subprocess


from hub.config import Config
from hub.git_ctx import GitCtx
from hub.notifier import notify


class EmacsMissingServiceTemplate(Exception): ...

LOAD_CMD = "launchctl load ~/Library/LaunchAgents/hub_sync.plist"
START_CMD = "launchctl start hub_sync"

EMACS_SERVICE_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>hub_nsync</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/$(whoami)/dev/python/hub/hello.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>
0
    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/hub.sync.out</string>

    <key>StandardErrorPath</key>
    <string>/tmp/hub.sync.err</string>
</dict>
</plist>
    """

@notify("emacs-sync", "Emacs configs - pulling")
def pull(cfg: Config) -> str:
    with GitCtx(cfg) as repo:
        repo.remote().pull()
        try:
            os.symlink(f"{cfg.repositoy_path}/init.el", "/Users/wmb/.emacs.d/init.el")
        except FileExistsError:
            logging.info("symlink exists")
        return "Emacs configs pulled"

    
@notify("emacs-sync", "Emacs configs - pushing")
def push(cfg: Config) -> str:
    with GitCtx(cfg) as repo:
        for file in cfg.files_to_track:
            repo.git.add(file)

        now = datetime.now()
        formatted_date = now.strftime("%d-%m-%Y-%H-%M-%S")
        repo.index.commit(formatted_date)
        origin = repo.remote(name="origin")
        origin.push()
        del origin
    return "Emacs configs pushed"


def setup_emacs_service_plist() -> str:    
    full_path = f"{os.path.expanduser("~")}/Library/LaunchAgents"
    os.makedirs(full_path, exist_ok=True)
    with open(f"{full_path}/hub_sync.plist", "w") as plist:
        plist.write(EMACS_SERVICE_TEMPLATE)
    return f"{full_path}/hub_sync.plist"


@notify("emacs-sync", "Emacs configs - starting server")
def start_emacs_service(template_path: str) -> str:
    if not os.path.exists(template_path):
        raise EmacsMissingServiceTemplate
    
    try:
        _ = subprocess.run(
            LOAD_CMD, shell=True, capture_output=True, text=True, check=True
        )
        result = subprocess.run(
            START_CMD, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as err:
        print(err.stderr)
        return err.stderr
 
