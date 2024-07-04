import os
import sys
import boto3
import yaml


def load_conf_file(filepath="~/.ssh/ec2-ssh-config.yaml"):
    """Load configuration file."""
    expanded_filepath = os.path.expanduser(filepath)

    try:
        with open(expanded_filepath, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        print(f"Config file not found at {expanded_filepath}. Error: {e}")
        raise SystemExit


def list_ec2_instances(env, region_name, name_prefix=""):
    """
    In this version of the function, when an exception is
    encountered, an error message is printed and an empty list is returned.
    This ensures that list_ec2_instances always returns a list,
    which allows you to use the len() function on its return value.
    """
    session = boto3.Session(profile_name=env)

    try:
        ec2_client = session.client("ec2", region_name=region_name)
        instances_info = []
        paginator = ec2_client.get_paginator("describe_instances")

        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance["State"]["Name"] == "running" or instance["State"]["Name"] == "pending":
                        name_tag = next(
                            (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), None
                        )

                        if name_prefix and (name_tag is None or not name_tag.startswith(name_prefix)):
                            continue

                        instance_id = instance["InstanceId"]
                        private_ip = instance.get("PrivateIpAddress", "N/A")
                        launch_time = instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S")

                        instances_info.append([instance_id, name_tag, private_ip, launch_time])

        return instances_info
    except Exception as e:
        print(e)
        return []


def connect_to_ssh_server(bastion, username, key, host_name, host_ip):
    """
    Connect to an SSH server using the os.system command.

    :param hostname: The address of the SSH server.
    :param username: The username for the SSH connection.
    :param key: The path to the SSH private key.
    :param host_name: The name of the host to connect to.
    :param host_ip: The IP address of the host to connect to.
    :return: None
    """
    # Construct the SSH command
    print(f"Connecting to {host_name} ({host_ip}) via {bastion}. Please approve DUA prompt.............")
    ssh_command = f"ssh -i {key} -J {username}@{bastion} {username}@{host_ip}"

    # Execute the SSH command
    exit_status = os.system(ssh_command)

    # If the SSH command failed, raise a SystemExit exception
    if exit_status != 0:
        print(f"An error occurred: {exit_status}")
        raise SystemExit(exit_status)
