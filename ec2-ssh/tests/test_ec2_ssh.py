#!/usr/bin/env python

"""Tests for `ec2_ssh` package."""

import pytest

from ec2_ssh.ec2_ssh import list_ec2_instances, connect_to_ssh_server
from ec2_ssh.cli import main
from unittest.mock import patch, MagicMock


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get("https://github.com/audreyr/cookiecutter-pypackage")


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert "GitHub" in BeautifulSoup(response.content).title.string


class MockPaginator:
    def paginate(self):
        return [
            {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-0123456789abcdef0",
                                "State": {"Name": "running"},
                                "Tags": [{"Key": "Name", "Value": "MyTestInstance"}],
                                "LaunchTime": MagicMock(strftime=lambda x: "2023-03-04 16:52:21"),
                                "PrivateIpAddress": "10.110.14.230",
                            }
                        ]
                    }
                ]
            }
        ]


@pytest.fixture
def ec2_client():
    with patch("boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_paginator.return_value = MockPaginator()
        yield mock_client


def test_list_ec2_instances(ec2_client):
    env = "dev"
    region_name = "eu-west-1"
    name_prefix = "MyTest"
    expected_instances = [["i-0123456789abcdef0", "MyTestInstance", "10.110.14.230", "2023-03-04 16:52:21"]]
    instances = list_ec2_instances(env, region_name, name_prefix)
    assert instances == expected_instances
    ec2_client.get_paginator.assert_called_with("describe_instances")


# @patch('boto3.Session')
# def test_list_ec2_instances_exception(mock_session):
#     # Mock the return value of get_paginator to raise an exception
#     mock_session.return_value.client.return_value.get_paginator.side_effect = Exception('Test exception')

#     # Call the function with test arguments and expect an empty list
#     instances = list_ec2_instances('test_env', 'test_region')

#     # Verify that an empty list was returned
#     assert instances == []


# @patch('os.system', return_value=0)
# def test_connect_to_ssh_server_success(mock_system):
#     # Call the function with test arguments
#     connect_to_ssh_server('test_bastion', 'test_user', 'test_key', 'test_host', 'test_ip')

#     # Verify that os.system was called with the correct argument
#     mock_system.assert_called_once_with('ssh -i test_key -J test_user@test_bastion test_user@test_ip')


# @patch('os.system', return_value=1)
# def test_connect_to_ssh_server_failure(mock_system):
#     # Call the function with test arguments and expect a SystemExit exception
#     with pytest.raises(SystemExit):
#         connect_to_ssh_server('test_bastion', 'test_user', 'test_key', 'test_host', 'test_ip')

#     # Verify that os.system was called with the correct argument
#     mock_system.assert_called_once_with('ssh -i test_key -J test_user@test_bastion test_user@test_ip')


# @patch('os.system', return_value=2)
# def test_connect_to_ssh_server_other_failure(mock_system):
#     # Call the function with test arguments and expect a SystemExit exception
#     with pytest.raises(SystemExit):
#         connect_to_ssh_server('test_bastion', 'test_user', 'test_key', 'test_host', 'test_ip')

#     # Verify that os.system was called with the correct argument
#     mock_system.assert_called_once_with('ssh -i test_key -J test_user@test_bastion test_user@test_ip')


# Mocks for the external dependencies and functions
# @pytest.fixture
# def mock_args_prod():
#     return MagicMock(profile="prd", name=None, region=None)

# @pytest.fixture
# def mock_args_non_prod():
#     return MagicMock(profile="dev", name=None, region=None)

# @pytest.fixture
# def mock_config():
#     return {
#         "username": "user.test",
#         "prod_key": "~/.ssh/test_key",
#         "non-prod_key": "~/.ssh/test_key",
#         "bastion": "bastion.host"
#     }


@pytest.fixture
def mock_instances():
    return [
        ["i-1234567890abcdef0", "test-instance-1", "10.0.0.1"],
        ["i-0987654321fedcba0", "test-instance-2", "10.0.0.2"],
    ]
