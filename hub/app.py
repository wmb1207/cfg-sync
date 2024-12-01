import os


import logging
import socket
from hub.config import Config
import hub.emacs as emacs
from hub.notifier import send_notification


class NoRepoCloned(Exception): ...


class MissingConfigs(Exception): ...

def handler(conn: socket.socket, cfg: Config):
    data: bytes = conn.recv(1024)
    if not data:
        return

    msg: str = data.decode("utf-8")
    match msg:
        case "pull":
            print("PULLING")
            send_notification("emacs sync", "pulling configs")
            emacs.pull(cfg)
            send_notification("emacs sync", "pulled configs")
        case "push":
            emacs.push(cfg)
        case "emacs":
            emacs.start_emacs_service(emacs.setup_emacs_service_plist())
        case _:
            logging.info(f"Invalid command {data}")
    return


def server(cfg: Config, socket_path: str = "/Users/wmb/.emacs_sync"):
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    logging.info("Running server")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(socket_path)
        server_socket.listen()
        while True:
            conn, _ = server_socket.accept()
            with conn:
                print(f"Connection accepted")
                handler(conn, cfg)


def main():
    cfg = Config(
        repository="git@github.com:wmb1207/emacs-cfg.git",
        repositoy_path="/Users/wmb/dev/cfgs/emacs-cfg",
        files_to_track=["init.el"],
    )

    server(cfg)
