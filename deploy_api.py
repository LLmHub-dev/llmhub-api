#!/usr/bin/env python3

import argparse
import subprocess
import sys


def deploy(api_type):
    # Map the argument to the correct function app name
    mapping = {"dv": "llmhub-dv-api", "sg": "llmhub-sg-api", "pd": "llmhub-pd-api"}

    # Validate the input
    if api_type not in mapping:
        print("Invalid argument. Please use 'dv', 'sg', or 'pd'.")
        sys.exit(1)

    app_name = mapping[api_type]
    command = ["func", "azure", "functionapp", "publish", app_name, "--python"]

    print(f"Deploying {app_name} using command: {' '.join(command)}")

    try:
        subprocess.run(command, check=True)
        print("Deployment successful!")
    except subprocess.CalledProcessError as e:
        print("An error occurred during deployment.")
        sys.exit(e.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Automate deployment of API based on the provided argument."
    )
    parser.add_argument(
        "api",
        choices=["dv", "sg", "pd"],
        help="API type to deploy: 'dv' for llmhub-dv-api, 'sg' for llmhub-sg-api, 'pd' for llmhub-pd-api",
    )
    args = parser.parse_args()
    deploy(args.api)


# python deploy_api.py dv
# python deploy_api.py sg
# python deploy_api.py pd

if __name__ == "__main__":
    main()
