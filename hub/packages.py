from __future__ import annotations


from dataclasses import dataclass, asdict

import os
import logging
import json
import subprocess
from typing import TypedDict


@dataclass
class Package:
    name: str
    version: str | None = None

    def __str__(self) -> str:
        if self.version:
            return f"{self.name}@{self.version}"
        return self.name
        


class JsonStorage(TypedDict):
    cask: list[Package]
    packages: list[Package]


class PackageInstaller:
    """
     class to manage the installation of packages and casks using Homebrew.

    Attributes:
        persistance_file (str): The filename for storing package data.
        _casks (list[Package]): A list of cask packages to install.
        _packages (list[Package]): A list of regular packages to install.
        cask_stdout (str): Standard output from the cask installation command.
        packages_stdout (str): Standard output from the package installation command.
        cask_stderr (str): Standard error from the cask installation command.
        packages_stderr (str): Standard error from the package installation command.

    Methods:
        __init__(cask=[], packages=[]): Initializes the PackageInstaller with optional lists of casks and packages.
        run(): Executes the installation commands for casks and packages.
        _store(): Stores the current state of casks and packages to a JSON file.
        add_cask(cask: Package): Adds a cask to the list of casks to be installed.
        add_package(package: Package): Adds a package to the list of packages to be installed.
        store(): Serializes the current state of casks and packages to a JSON file.
        load() -> PackageInstaller: Loads the state from the persistent file and returns a PackageInstaller instance.
        cask_cmd (str): Constructs the command string for installing casks.
        packages_cmd (str): Constructs the command string for installing packages.
        store_result(): Saves the stdout and stderr from the installation commands to separate files.
        persistance_path() -> str: Returns the file path for the persistence storage file.
    """

    persistance_file = "hub.packages.json"

    _casks: list[Package]
    _packages: list[Package]

    cask_stdout: str
    packages_stdout: str

    cask_stderr: str
    packages_stderr: str

    def __init__(self, cask: list[Package] = [], packages: list[Package] = []):
        self._casks = cask
        self._packages = packages
    
    def run(self):
        try:
            result = subprocess.run(
                self.cask_cmd, shell=True, capture_output=True, text=True, check=True
            )
            self.cask_stdout = result.stdout
            self.cask_stderr = result.stderr
        except subprocess.CalledProcessError as err:
            logging.error(err)
            self.cask_stderr = err.stderr
            self.cask_stdout = err.stdout

        try:
            result = subprocess.run(
                self.packages_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            )
            self.packages_stdout = result.stdout
            self.packages_stderr = result.stderr
        except subprocess.CalledProcessError as err:
            logging.error(err)
            self.packages_stderr = err.stderr
            self.packages_stdout = err.stdout

    def _store(self):
        with open(self.persistance_path(), "w") as file:
            to_store = {
                "casks": self._casks,
                "packages": self._packages
            }

            file.write(json.dumps(to_store))

    def add_cask(self, cask: Package):
        self._casks.append(cask)

    def add_package(self, package: Package):
        self._packages.append(package)

    def store(self):
        to_store = {
            "cask": [asdict(c) for c in self._casks],
            "packages": [asdict(c) for c in self._packages],
        }

        with open(self.persistance_path(), "w") as output:
            output.write(json.dumps(to_store))

    @classmethod
    def load(cls) -> PackageInstaller:
        json_data: JsonStorage

        with open(cls.persistance_path(), "r") as file:
            json_data = json.load(file)

        return cls(json_data["cask"], json_data["packages"])

    @property
    def cask_cmd(self) -> str:
        return f"brew install --cask {" ".join([str(c) for c in self._casks])}"

    @property
    def packages_cmd(self) -> str:
        return f"brew install --cask {" ".join([str(p) for p in self._packages])}"

    def store_result(self):
        with open("casks.stdout", "w") as output:
            output.write(self.cask_stdout)

        with open("casks.stderr", "w") as output:
            output.write(self.cask_stderr)

        with open("packages.stdout", "w") as output:
            output.write(self.cask_stdout)
    
        with open("packages.stderr", "w") as output:
            output.write(self.cask_stderr)

    @classmethod
    def persistance_path(cls) -> str:
        home_path = os.path.expanduser("~")
        return f"{home_path}/.config/{cls.persistance_file}"
        
