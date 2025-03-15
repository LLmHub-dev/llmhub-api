import subprocess

def kill_process_on_port(port):
    # 1. Run netstat to find processes listening on the given port.
    #    The -a flag displays all connections and listening ports
    #    The -n flag displays addresses and port numbers in numerical form
    #    The -o flag displays the owning process ID associated with each connection
    command = ["netstat", "-ano"]
    result = subprocess.run(command, capture_output=True, text=True)

    lines = result.stdout.splitlines()

    for line in lines:
        # Each line with a listening process typically looks like:
        # "  TCP    0.0.0.0:7071       0.0.0.0:0     LISTENING       <PID>"
        # We'll check if ":7071" is in the line to identify the relevant line.
        if f":{port} " in line:
            # Split the line into tokens
            tokens = line.split()
            # The last token is the PID in most netstat lines
            pid = tokens[-1]
            
            try:
                # 2. Kill the process using taskkill
                kill_command = ["taskkill", "/PID", pid, "/F"]
                subprocess.run(kill_command, check=True)
                print(f"Process with PID {pid} on port {port} has been terminated.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to kill process with PID {pid}. Error: {e}")

if __name__ == "__main__":
    kill_process_on_port(7071)
