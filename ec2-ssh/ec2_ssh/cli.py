"""Console script for ec2_ssh."""

import argparse
import sys
from pick import pick
from .ec2_ssh import list_ec2_instances, load_conf_file, connect_to_ssh_server


def create_arg_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(description="Find and connect to an EC2 instance via SSH.")
    parser.add_argument(
        "--profile",
        help="Use a specific profile from your credential file",
        required=True,
        choices=["dev", "sha", "sbx", "nft", "prd"],
    )
    parser.add_argument("--name", help="Filter instances by name prefix", required=False)
    parser.add_argument(
        "--region", help="The AWS region to use. Default eu-west-1", required=False, default="eu-west-1"
    )
    return parser


def get_ssh_key(profile, config):
    """Get the appropriate SSH key based on profile."""
    return config["prod_key"] if profile == "prd" else config["non-prod_key"]


def user_pick_instance(instances, title):
    return pick(instances, title=title, multiselect=False, min_selection_count=1, indicator="=>")[0]


def main():
    """Main function to execute the script logic."""
    try:
        parser = create_arg_parser()
        args = parser.parse_args()

        config = load_conf_file()

        # Fetch the list of instances
        instances = list_ec2_instances(args.profile, name_prefix=args.name, region_name=args.region)

        username = config["username"]
        key = get_ssh_key(args.profile, config)
        bastion = config["bastion"]

        # If there are no instances, print a message and exit
        if len(instances) == 0 and not instances:
            print("No instances found")
            sys.exit(1)

        # If there are instances, let the user pick one
        selected_instance = user_pick_instance(instances, "Please choose the instance to connect to:")
        select_host_name = selected_instance[1]
        select_host_ip = selected_instance[2]

        # Connect to the selected instance
        connect_to_ssh_server(bastion, username, key, select_host_name, select_host_ip)
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
