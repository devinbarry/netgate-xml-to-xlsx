"""Nox sessions."""

import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox

python_versions = [
    "3.9",
]
nox.options.reuse_existing_virtualenv = True
nox.needs_version = ">= 2022.1.7"
nox.options.sessions = ("format",)


try:
    from nox_poetry import Session, session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.

    Please install it using the following command:

    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None


@session(name="format", python=python_versions[0])
def format(session: Session) -> None:
    """Standard formatting."""
    session.install("black", "isort")
    session.run("isort", ".")
    session.run("black", ".")
