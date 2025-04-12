#!/usr/bin/env python3
"""
Script Name: transfer.py
Date:        2025-04-12
Author:      Blaine Winslow
Description: A general file/folder transfer package using CLI. This script transfers files or folders
             from a local machine to a remote machine using rsync over SSH.
Inputs:      source (local file/folder), destination user (SSH username), destination host (IP address),
             destination remote path.
Outputs:     Files/folders transferred to the destination path on the remote server.
Parameter Descriptions:
    - source: Local file or directory to transfer.
    - user: Remote SSH username.
    - host: Remote host IP address.
    - remote_path: Destination path on the remote server.
Summary:     Validates inputs using regex (for IP validation) and OS checks; prompts for corrections if any error
             is detected. After successful validation, it performs the file transfer via rsync.
Modification Log:
    2025-04-12: Initial version.
"""

import os
import re
import subprocess
import sys
import argparse

def validate_ip(ip):
    """
    Validate the IP address using a regex pattern.
    Returns True if valid, otherwise False.
    """
    ip_pattern = re.compile(
        r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
    )
    return ip_pattern.match(ip) is not None

def validate_local_path(path):
    """
    Check if the given local path exists (file or directory).
    """
    return os.path.exists(path)

def prompt_for_input(prompt_message, validation_func, error_message):
    """
    Prompt the user repeatedly until validation_func returns True.
    """
    while True:
        value = input(prompt_message).strip()
        if validation_func(value):
            return value
        else:
            print(f"Error: {error_message}. Please try again.")

def get_arguments():
    """
    Parse command line arguments and interactively prompt for corrections if necessary.
    """
    parser = argparse.ArgumentParser(
        description="General file/folder transfer CLI utility using rsync over SSH."
    )
    parser.add_argument("source", nargs="?", help="Local source path (file or directory) to transfer")
    parser.add_argument("--user", "-u", help="Remote SSH username", default="cbwinslow")
    parser.add_argument("--host", "-H", help="Remote host IP address", default="192.168.6.69")
    parser.add_argument("--remote_path", "-r", help="Destination path on remote host", default="/home/cbwinslow/")
    args = parser.parse_args()

    # Validate the source path
    if not args.source or not validate_local_path(args.source):
        if args.source:
            print(f"Error: Provided source '{args.source}' does not exist.")
        args.source = prompt_for_input("Enter a valid local source path: ", validate_local_path, "Path does not exist")

    # Validate the destination host IP
    if not validate_ip(args.host):
        print(f"Error: Provided host IP '{args.host}' is invalid.")
        args.host = prompt_for_input("Enter a valid IP address for the remote host: ", validate_ip, "IP address format is invalid")

    return args

def main():
    args = get_arguments()
    source = args.source
    dest_user = args.user
    dest_host = args.host
    dest_path = args.remote_path

    # Construct the rsync command
    rsync_command = [
        "rsync", "-avh", "--progress", "--partial", "--inplace",
        source, f"{dest_user}@{dest_host}:{dest_path}"
    ]

    print("Starting file/folder transfer using rsync...")
    print(f"Source: {source}")
    print(f"Destination: {dest_user}@{dest_host}:{dest_path}")

    try:
        result = subprocess.run(rsync_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Transfer failed with error code {e.returncode}.")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: rsync command not found. Please ensure rsync is installed.")
        sys.exit(1)

    print("Transfer completed successfully!")

if __name__ == "__main__":
    main()
