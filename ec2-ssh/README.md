# ec2-ssh

ec2-ssh, a Python utility that allows users to find AWS EC2 instances by their tag names and establish an SSH connection to them. This tool streamlines the process of identifying the correct instance and connecting to it without having to manually search through the AWS console or use multiple AWS CLI commands.

## Features

- Search for EC2 instances by tag name.
- List instances matching the search criteria.
- SSH into a selected EC2 instance directly from the command line.
- 
## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- Boto3 (AWS SDK for Python), pick and PyYAML packages.
- AWS CLI configured with the necessary access
- ec2-ssh config containing following config:

File: ~/.ssh/ec2-ssh-config.yaml

```
---
username: shirwa.hersi
non-prod_key: ~/.ssh/modulr-non-prod
prod_key: ~/.ssh/modulr-prod
bastion: bastion.aws.modulrfinance.io

```


## Installation

From pip:

```
pip3 install .
```

## Usage

```
ec2-ssh --help
usage: ec2-ssh [-h] --profile {dev,sha,sbx,nft,prd} [--name NAME] [--region REGION]

Find and connect to an EC2 instance via SSH.

options:
  -h, --help            show this help message and exit
  --profile {dev,sha,sbx,nft,prd}
                        Use a specific profile from your credential file
  --name NAME           Filter instances by name prefix
  --region REGION       The AWS region to use. Default eu-west-1

```

![Basic Usage](docs/usage.gif)