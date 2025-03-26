#!/usr/bin/env python3
import os
import sys
import stat
import urllib.request
import platform
import subprocess

print("Installing foundryup...")

# Determine base directory.
base_dir = os.environ.get("XDG_CONFIG_HOME", os.environ.get("HOME"))
if not base_dir:
    sys.exit("Error: HOME environment variable not set.")

# Set directories.
foundry_dir = os.environ.get("FOUNDRY_DIR", os.path.join(base_dir, ".foundry"))
foundry_bin_dir = os.path.join(foundry_dir, "bin")
foundry_man_dir = os.path.join(foundry_dir, "share", "man", "man1")

# URL and destination for the foundryup binary.
bin_url = "https://raw.githubusercontent.com/foundry-rs/foundry/master/foundryup/foundryup"
bin_path = os.path.join(foundry_bin_dir, "foundryup")

# Create the .foundry bin directory if it doesn't exist.
os.makedirs(foundry_bin_dir, exist_ok=True)

# Download the binary.
try:
    with urllib.request.urlopen(bin_url) as response:
        data = response.read()
    with open(bin_path, "wb") as f:
        f.write(data)
except Exception as e:
    sys.exit(f"Error downloading foundryup: {e}")

# Make the binary executable.
st = os.stat(bin_path)
os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

# Create the man directory.
os.makedirs(foundry_man_dir, exist_ok=True)

# Determine the shell and corresponding profile file.
shell = os.environ.get("SHELL", "")
pref_shell = None
profile = None

if shell.endswith("zsh"):
    # Use ZDOTDIR if set; otherwise default to $HOME.
    zdotdir = os.environ.get("ZDOTDIR", os.environ.get("HOME"))
    profile = os.path.join(zdotdir, ".zshenv")
    pref_shell = "zsh"
elif shell.endswith("bash"):
    profile = os.path.join(os.environ.get("HOME"), ".bashrc")
    pref_shell = "bash"
elif shell.endswith("fish"):
    profile = os.path.join(os.environ.get("HOME"), ".config", "fish", "config.fish")
    pref_shell = "fish"
elif shell.endswith("ash"):
    profile = os.path.join(os.environ.get("HOME"), ".profile")
    pref_shell = "ash"
else:
    sys.exit("foundryup: could not detect shell, manually add {} to your PATH.".format(foundry_bin_dir))

# Check if foundry_bin_dir is already in PATH.
current_path = os.environ.get("PATH", "")
if foundry_bin_dir not in current_path.split(os.pathsep):
    try:
        # Append the PATH modification to the profile file.
        with open(profile, "a") as f:
            f.write("\n")
            if pref_shell == "fish":
                # For fish shell.
                f.write(f"fish_add_path -a {foundry_bin_dir}\n")
            else:
                # For other shells.
                f.write(f'export PATH="$PATH:{foundry_bin_dir}"\n')
    except Exception as e:
        sys.exit(f"Error updating profile file {profile}: {e}")

# Warn MacOS users about libusb if necessary.
if (os.environ.get("OSTYPE", "").startswith("darwin") or platform.system() == "Darwin"):
    libusb_paths = [
        "/usr/local/opt/libusb/lib/libusb-1.0.0.dylib",
        "/opt/homebrew/opt/libusb/lib/libusb-1.0.0.dylib",
    ]
    if not any(os.path.exists(path) for path in libusb_paths):
        print("\nwarning: libusb not found. You may need to install it manually on MacOS via Homebrew (brew install libusb).")

# If using bash, update the current environment and run foundryup.
if pref_shell == "bash":
    print("\nDetected your preferred shell is bash. Updating PATH and running 'foundryup'...")
    # Update the environment so that foundryup can be found.
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + foundry_bin_dir
    try:
        subprocess.run(["foundryup"], check=True)
    except FileNotFoundError:
        sys.exit("Error: foundryup not found in PATH after updating it.")

print()
print(f"Detected your preferred shell is {pref_shell} and added foundryup to PATH.")
print(f"Run 'source {profile}' or start a new terminal session to use foundryup.")
print("Then, simply run 'foundryup' to install Foundry.")
