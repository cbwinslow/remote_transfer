/**
 * Script Name: transfer.ts
 * Date:        2025-04-12
 * Author:      Blaine Winslow
 * Description: A general file/folder transfer CLI utility using rsync over SSH.
 * Inputs:      source (local file/folder), remote SSH user, remote host IP, remote destination path.
 * Outputs:     Files/folders transferred to the remote destination.
 * Parameter Descriptions:
 *    - source: Local file or directory to transfer.
 *    - user: Remote SSH username.
 *    - host: Remote host IP address.
 *    - remotePath: Destination path on the remote host.
 * Summary:     Validates inputs using regex and filesystem checks. If errors occur, prompts the user for
 *              corrections before transferring files using rsync.
 * Modification Log:
 *    2025-04-12: Initial version.
 */

import * as fs from 'fs';
import * as readline from 'readline';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

/**
 * Validate the IP address using regex.
 * @param ip - The IP address string to validate.
 * @returns boolean indicating validity.
 */
function validateIp(ip: string): boolean {
    const ipPattern = /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$/;
    return ipPattern.test(ip);
}

/**
 * Validate that the local path exists.
 * @param path - File or directory path.
 * @returns boolean indicating whether the path exists.
 */
function validatePath(path: string): boolean {
    return fs.existsSync(path);
}

/**
 * Prompt the user for input using the readline interface.
 * @param query - The prompt message.
 * @returns Promise resolving to the user input.
 */
function prompt(query: string): Promise<string> {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    return new Promise((resolve) => {
        rl.question(query, (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

/**
 * Main async function that performs validation and initiates the transfer.
 */
async function main() {
    const args = process.argv.slice(2);
    let source = args[0] || '';
    let destUser = args[1] || 'cbwinslow';
    let destHost = args[2] || '192.168.6.69';
    let remotePath = args[3] || `/home/${destUser}/`;

    // Validate the source path
    while (!validatePath(source)) {
        console.log(`Error: Source path '${source}' does not exist.`);
        source = await prompt("Enter a valid local source path: ");
    }

    // Validate the remote host IP
    while (!validateIp(destHost)) {
        console.log(`Error: Destination host IP '${destHost}' is invalid.`);
        destHost = await prompt("Enter a valid remote host IP address: ");
    }

    console.log("Starting file/folder transfer using rsync over SSH...");
    console.log(`Source: ${source}`);
    console.log(`Destination: ${destUser}@${destHost}:${remotePath}`);

    // Construct the rsync command string
    const rsyncCommand = `rsync -avh --progress --partial --inplace "${source}" ${destUser}@${destHost}:"${remotePath}"`;

    try {
        const { stdout, stderr } = await execPromise(rsyncCommand);
        console.log(stdout);
        if (stderr) {
            console.error(stderr);
        }
        console.log("Transfer completed successfully!");
    } catch (error: any) {
        console.error("Error: Transfer failed.", error);
        process.exit(1);
    }
}

main();
