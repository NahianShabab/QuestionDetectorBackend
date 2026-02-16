import subprocess
from pathlib import Path

# Replace this path with your venv's python.exe if you want hardcoded
VENV_PYTHON = Path(r"E:\Question Website\backend\venv\Scripts\python.exe")
SCRIPT = Path(r"E:\Question Website\backend\create_user.py")

for i in range(1, 11):
    username = f"composer{i}"
    password = f"composer{i}"
    first_name = f"Composer{i}"
    user_role = "composer"

    print(f"Creating {username}...")

    cmd = [
        str(VENV_PYTHON), str(SCRIPT),
        "--username", username,
        "--password", password,
        "--first-name", first_name,
        "--user-role", user_role,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"{username} created successfully.")
    else:
        print(f"Failed to create {username}:")
        print(result.stderr or result.stdout)
