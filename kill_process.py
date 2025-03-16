import subprocess
import sys
import os


def kill_process_on_port(port):
    """
    Find and kill any process running on the specified port.
    Cross-platform compatible (Windows, Linux, macOS).
    """
    print(f"Checking for processes on port {port}...")

    # Determine the operating system
    if sys.platform.startswith("win"):
        # Windows
        try:
            # Find process using netstat
            command = ["netstat", "-ano"]
            result = subprocess.run(command, capture_output=True, text=True)

            pid = None
            for line in result.stdout.splitlines():
                if f":{port} " in line and "LISTENING" in line:
                    # Extract PID from the end of the line
                    parts = line.strip().split()
                    pid = parts[-1]
                    break

            if pid:
                # Kill the process
                kill_command = ["taskkill", "/PID", pid, "/F"]
                subprocess.run(kill_command, check=True)
                print(f"Process with PID {pid} on port {port} has been terminated.")
                return True
            else:
                print(f"No process found using port {port}.")
                return False

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return False
    else:
        # Linux/macOS
        try:
            # Find process using lsof
            find_command = ["lsof", "-i", f":{port}"]
            result = subprocess.run(find_command, capture_output=True, text=True)

            if result.stdout.strip():
                # Extract PID from second column of lsof output
                lines = result.stdout.splitlines()
                if len(lines) > 1:  # Skip header line
                    pid = lines[1].split()[1]
                    # Kill the process
                    kill_command = ["kill", "-9", pid]
                    subprocess.run(kill_command, check=True)
                    print(f"Process with PID {pid} on port {port} has been terminated.")
                    return True
                else:
                    print(f"No process found using port {port}.")
                    return False
            else:
                print(f"No process found using port {port}.")
                return False

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return False
        except FileNotFoundError:
            print(
                "Error: 'lsof' command not found. Please install it or use another method."
            )
            return False


if __name__ == "__main__":
    kill_process_on_port(7071)
