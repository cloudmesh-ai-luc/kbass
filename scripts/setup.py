"""Initialize a CloudOps AI installation without overwriting existing data."""

from pathlib import Path
import os
import secrets

ROOT = Path(__file__).resolve().parent.parent
template = ROOT / ".env.example"
destination = ROOT / ".env.cloudops"

if not template.is_file():
    raise SystemExit("ERROR: .env.example is missing.")

if destination.exists() or destination.is_symlink():
    print("Existing .env.cloudops preserved.")
else:
    content = template.read_text()

    replacements = {
        "REPLACE_WITH_STRONG_RANDOM_TOKEN": secrets.token_urlsafe(48),
        "REPLACE_WITH_INDEPENDENT_RANDOM_SECRET": secrets.token_urlsafe(48),
    }

    for placeholder, value in replacements.items():
        if content.count(placeholder) != 1:
            raise SystemExit(
                f"ERROR: Expected exactly one {placeholder} placeholder."
            )
        content = content.replace(placeholder, value)

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(destination, flags, 0o600)

    with os.fdopen(fd, "w") as file:
        file.write(content)

    print("Created private .env.cloudops with generated credentials.")

for directory in ("data", "prometheus/targets"):
    path = ROOT / directory
    path.mkdir(parents=True, exist_ok=True)
    print(f"Directory ready: {directory}")

print("CloudOps AI setup completed.")
