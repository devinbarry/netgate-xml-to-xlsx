"""Nox sessions."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox

package = "netgate_xml_to_xlsx"
# When defining multiple versions, put the lowest version first for compatibility.
python_versions = [
    "3.10",
]
# nox.options.reuse_existing_virtualenv = True
nox.needs_version = ">= 2022.1.7"
nox.options.sessions = ("build",)


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
    session.install("pyproject-flake8")
    session.run("pflake8", f"src/{package}")


@session(name="flakeheaven", python=python_versions[0])
def flakeheaven(session: Session) -> None:
    """Aggressive flaking."""
    format(session)
    session.install(
        "flakeheaven",
        "flake8-aaa",
        "flake8-2020",
        "flake8-bandit",
        "flake8-broken-line",
        "flake8-bugbear",
        "flake8-builtins",
        "flake8-comprehensions",
        "flake8-docstrings",
        "flake8-eradicate",
        "flake8-executable",
        "flake8-expression-complexity",
        "flake8-functions",
        "flake8-logging-format",
        "flake8-mutable",
        "flake8-printf-formatting",
        "flake8-pylint",
        "flake8-pytest-style",
        "flake8-pytest",
        ".",
    )
    session.run("flakeheaven", "plugins")
    session.run("flakeheaven", "lint", f"src/")


@session(name="pylint", python=python_versions[0])
def pylint(session: Session) -> None:
    """
    Standalone pylint.

    I like to occasionally run pylint by itself to:
        - get different reports
        - see the quality code
        - run other pylint plugins
    """
    session.install("pylint", "perflint")
    session.run(
        "pylint",
        "--rcfile=pylint.rc",
        "--load-plugins=perflint",
        f"src/{package}",
    )


@session(name="security", python=python_versions[0])
def security(session: Session) -> None:
    """Standard security checks."""
    session.install("bandit", "safety")
    session.run("bandit", "-c=pyproject.toml", "-r", f"src/{package}")
    session.run("safety", "check")


@session(name="test", python=python_versions)
def test(session: Session) -> None:
    """Pytest."""
    session.poetry.installroot()
    session.install("pytest")
    session.run("pytest", ".")


@session(name="mypy", python=python_versions)
def mypy(session: Session) -> None:
    """Type check the module."""
    session.install("mypy", "mypy-extensions")
    session.run("mypy", "-p", package)


@session(name="build", python=python_versions[0])
def build(session: Session) -> None:
    """
    Build package for release.

    Only need one build for all supported versions.
    """
    flake8(session)
    security(session)
    test(session)
    session.poetry.build_package(distribution_format="wheel")
