"""Nox sessions."""

import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox

package = "netgate_xml_to_xlsx"
python_versions = [
    "3.9",
]
nox.options.reuse_existing_virtualenv = True
nox.needs_version = ">= 2022.1.7"
nox.options.sessions = ("flake8",)


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


@session(name="flake8", python=python_versions)
def flake8(session: Session) -> None:
    """Simple flake8 check.

    Uses pyproject-flake8 which is a monkey-patched version that reads from pyproject.toml
    Format before flaking.
    """
    format(session)
    # session.notify("format")
    session.install("pyproject-flake8")
    session.run("pflake8", package)


@session(name="pylint", python=python_versions)
def pylint(session: Session) -> None:
    """Standard pylint. Format before linting."""
    format(session)
    session.install("pylint")
    session.run("pylint", "--rcfile", "pylint.rc", package)


@session(name="mypy", python=python_versions)
def mypy(session: Session) -> None:
    """Type check the module."""
    session.install("mypy")
    session.run("mypy", "-p", package)


@session(name="security", python=python_versions[0])
def security(session: Session) -> None:
    """Standard security checks."""
    session.install("bandit", "safety")
    session.run("bandit", ".")
    session.run("safety", "check")
