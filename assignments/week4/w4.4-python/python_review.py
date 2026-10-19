import os
import subprocess

import click


def greet(name):
    """Return a greeting for the supplied name."""
    return f"Hello, {name}! Welcome to COMP 488 W4.4."


def run_shell_commands():
    """Demonstrate two ways to run shell commands from Python."""
    print("\n1. Running ls with os.system():", flush=True)
    os.system("ls")

    print("\n2. Running ls -la with subprocess.run():", flush=True)
    subprocess.run(["ls", "-la"], check=True)


@click.command()
@click.option(
    "--name",
    default="Student",
    show_default=True,
    help="Name to include in the greeting.",
)
def main(name):
    """Review Python functions, arguments, and shell commands."""
    print(greet(name))
    run_shell_commands()


if __name__ == "__main__":
    main()
