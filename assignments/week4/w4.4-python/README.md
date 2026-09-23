# W4.4 – Review Python

## Overview

This assignment reviews Python virtual environments, package management,
functions, command-line arguments, and executing shell commands from Python.

## Environment Setup

I created a Python virtual environment using `venv`:

```bash
python3 -m venv ~/.venvs/comp488-w4-python
source ~/.venvs/comp488-w4-python/bin/activate
```

I created the environment in my WSL home directory because creating it
on the Windows-mounted drive caused a symbolic-link permission error.

## Package Management

I installed Click using `pip`:

```bash
python -m pip install click
```

I installed the OpenStack CLI using `pipx`:

```bash
pipx install python-openstackclient
```

Verified versions:

- Python: 3.14.4
- Click: 8.5.0
- pipx: 1.8.0
- OpenStack CLI via pipx: 10.3.0

`pip` installs packages into a Python environment, while `pipx` installs
command-line applications in isolated environments.

## Python Review

The `python_review.py` script demonstrates:

- Import statements
- Defining and calling functions
- A `main` block
- Command-line arguments using Click
- `os.system("ls")`
- `subprocess.run()`

## Testing

Successfully tested:

```bash
python python_review.py
python python_review.py --name Khalidou
python python_review.py --help
```

