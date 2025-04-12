#!/bin/bash
# Script Name: transfer.sh
# Date:        2025-04-12
# Author:      Blaine Winslow
# Description: A generalized CLI utility to transfer a file or directory over SSH using rsync.
# Inputs:      Source path, remote SSH username, remote host IP address, remote destination path.
# Outputs:     File/Folder transferred to the specified destination on the remote machine.
# Parameter Descriptions:
#    - Source path: Local file or directory to transfer.
#    - Remote user: SSH username for the remote host.
#    - Remote host: IP address of the remote host.
#    - Remote path: Destination directory on the remote host.
# Summary:     Validates inputs using regex and filesystem checks, prompting for corrections if errors occur.
# Modification Log:
#    2025-04-12: Initial version.

# Function: Validate IP address using regex
validate_ip() {
  local ip=$1
  if [[ $ip =~ ^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$ ]]; then
    return 0
  else
    return 1
  fi
}

# Function: Validate that the local path exists
validate_local_path() {
  local path="$1"
  [[ -e "$path" ]] && return 0 || return 1
}

# Function: Prompt for input until a valid value is provided
prompt_for_input() {
  local prompt_message="$1"
  local validation_func="$2"
  local error_message="$3"
  local input_value
  while true; do
    read -rp "$prompt_message" input_value
    if $validation_func "$input_value"; then
      echo "$input_value"
      return 0
    else
      echo "Error: $error_message. Please try again."
    fi
  done
}

# Parse arguments (positional parameters)
SRC_DIR="$1"
DEST_USER="${2:-cbwinslow}"
DEST_HOST="${3:-192.168.6.69}"
DEST_PATH="${4:-/home/cbwinslow/}"

# Validate the source directory
if ! validate_local_path "$SRC_DIR"; then
  echo "Provided source path '$SRC_DIR' does not exist or is invalid."
  SRC_DIR=$(prompt_for_input "Enter a valid local source path: " validate_local_path "Path does not exist")
fi

# Validate the remote host IP
if ! validate_ip "$DEST_HOST"; then
  echo "Provided remote host IP '$DEST_HOST' is invalid."
  DEST_HOST=$(prompt_for_input "Enter a valid remote host IP address: " validate_ip "IP address format is invalid")
fi

# Check SSH connectivity (non-interactive)
echo "Checking SSH connectivity to $DEST_USER@$DEST_HOST..."
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$DEST_USER@$DEST_HOST" "exit" &>/dev/null; then
  echo "Warning: SSH connection to $DEST_USER@$DEST_HOST could not be established. Verify SSH credentials and connectivity."
fi

# Start the transfer using rsync
echo "Starting transfer from '$SRC_DIR' to '$DEST_USER@$DEST_HOST:$DEST_PATH'..."
rsync -avh --progress --partial --inplace "$SRC_DIR" "$DEST_USER@$DEST_HOST:$DEST_PATH"
RSYNC_EXIT_CODE=$?

if [ $RSYNC_EXIT_CODE -eq 0 ]; then
  echo "Transfer completed successfully!"
else
  echo "Error: Transfer failed with exit code $RSYNC_EXIT_CODE."
  exit $RSYNC_EXIT_CODE
fi
