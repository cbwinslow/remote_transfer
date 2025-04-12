/*
Script Name: transfer.go
Date:        2025-04-12
Author:      Blaine Winslow
Description: A generalized CLI utility to transfer a file or directory over SSH using rsync.
Inputs:      source (local file/folder), remote SSH user, remote host IP, remote destination path.
Outputs:     Files/folders transferred to the specified destination on the remote machine.
Parameter Descriptions:
    - source: Local file or directory to transfer.
    - user: Remote SSH username (default: "cbwinslow").
    - host: Remote host IP address (default: "192.168.6.69").
    - remote: Destination path on the remote host (default: "/home/<user>/").
Summary:     Validates user inputs using regex and filesystem checks, prompting for corrections interactively if needed.
Modification Log:
    2025-04-12: Initial version.
*/

package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strings"
)

// validateIp validates an IP address using regex.
func validateIp(ip string) bool {
	ipRegex := regexp.MustCompile(`^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$`)
	return ipRegex.MatchString(ip)
}

// validateLocalPath checks if the file or directory exists.
func validateLocalPath(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

// promptForInput prompts the user to input a value.
func promptForInput(promptMessage string) string {
	reader := bufio.NewReader(os.Stdin)
	fmt.Print(promptMessage)
	text, _ := reader.ReadString('\n')
	return strings.TrimSpace(text)
}

func main() {
	// Define and parse command-line flags.
	sourcePtr := flag.String("source", "", "Local source path (file or directory) to transfer")
	userPtr := flag.String("user", "cbwinslow", "Remote SSH username")
	hostPtr := flag.String("host", "192.168.6.69", "Remote host IP address")
	remotePathPtr := flag.String("remote", "", "Destination path on remote host (default: /home/<user>/)")
	flag.Parse()

	source := *sourcePtr
	destUser := *userPtr
	destHost := *hostPtr
	remotePath := *remotePathPtr

	// Set default remote path if not provided.
	if remotePath == "" {
		remotePath = fmt.Sprintf("/home/%s/", destUser)
	}

	// Validate the source path.
	for !validateLocalPath(source) {
		fmt.Printf("Error: Source path '%s' does not exist.\n", source)
		source = promptForInput("Enter a valid local source path: ")
	}

	// Validate the remote host IP.
	for !validateIp(destHost) {
		fmt.Printf("Error: Destination host IP '%s' is invalid.\n", destHost)
		destHost = promptForInput("Enter a valid remote host IP address: ")
	}

	fmt.Println("Starting file/folder transfer using rsync over SSH...")
	fmt.Printf("Source: %s\n", source)
	fmt.Printf("Destination: %s@%s:%s\n", destUser, destHost, remotePath)

	// Construct the rsync command arguments.
	rsyncArgs := []string{
		"-avh", "--progress", "--partial", "--inplace",
		source, fmt.Sprintf("%s@%s:%s", destUser, destHost, remotePath),
	}

	// Execute the rsync command.
	cmd := exec.Command("rsync", rsyncArgs...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: Transfer failed with error: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Transfer completed successfully!")
}
