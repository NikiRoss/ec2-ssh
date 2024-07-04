import pytest
import argparse

from pick import pick
from ec2_ssh.cli import create_arg_parser, main, get_ssh_key, user_pick_instance
from ec2_ssh.ec2_ssh import load_conf_file, list_ec2_instances, connect_to_ssh_server
from unittest.mock import mock_open, patch, MagicMock


def test_parse_args():
    with patch("sys.argv", ["ec2_ssh", "--profile", "dev"]):
        parser = create_arg_parser()
        args = parser.parse_args()
        assert args.profile == "dev"

    with patch("sys.argv", ["ec2_ssh", "--profile", "dev", "--name", "test", "--region", "eu-west-1"]):
        parser = create_arg_parser()
        args = parser.parse_args()
        assert args.profile == "dev"
        assert args.name == "test"
        assert args.region == "eu-west-1"


# Mock YAML content
mock_yaml_data = """
username: test.test
non-prod_key: ~/.ssh/test_key
prod_key: ~/.ssh/test_key
bastion: test.test
"""


@pytest.fixture
def mock_yaml_file():
    with patch("builtins.open", mock_open(read_data=mock_yaml_data)):
        yield


def test_load_conf_file_success(mock_yaml_file):
    """Test loading configuration file."""
    with patch("os.path.expanduser") as mock_expanduser:
        mock_expanduser.return_value = "/fake/home/test/.ssh/ec2-ssh-config.yaml"

        # Call the actual function
        config = load_conf_file()

        # Assertions to check if the function is reading the correct values from the YAML file
        assert config["username"] == "test.test"
        assert config["non-prod_key"] == "~/.ssh/test_key"
        assert config["prod_key"] == "~/.ssh/test_key"
        assert config["bastion"] == "test.test"


def test_load_conf_file_file_not_found(capsys):
    with patch("os.path.expanduser") as mock_expanduser:
        mock_expanduser.return_value = "/fake/home/test/.ssh/ec2-ssh-config.yaml"

        # Patch the open function to raise a FileNotFoundError
        with patch("builtins.open", side_effect=FileNotFoundError):
            # Capturing the output to check if the correct message is printed
            with pytest.raises(SystemExit):
                load_conf_file()
            out, err = capsys.readouterr()
            assert "Config file not found at /fake/home/test/.ssh/ec2-ssh-config.yaml" in out


def test_get_ssh_key_prod():
    # Mock configuration for production profile
    mock_config = {"prod_key": "~/.ssh/prod/test_key", "non-prod_key": "~/.ssh/non_prod/test_key"}

    # Call the function with the 'prd' profile
    ssh_key = get_ssh_key("prd", mock_config)
    # Assert that the correct key is returned for the 'prd' profile
    assert ssh_key == "~/.ssh/prod/test_key"


def test_get_ssh_key_non_prod():
    # Mock configuration for non-production profile
    mock_config = {"prod_key": "~/.ssh/prod/test_key", "non-prod_key": "~/.ssh/non-prod/test_key"}
    # Call the function with a non-production profile
    ssh_key = get_ssh_key("dev", mock_config)
    # Assert that the correct key is returned for non-production profiles
    assert ssh_key == "~/.ssh/non-prod/test_key"


@patch("ec2_ssh.cli.pick")
def test_user_pick_instance(mock_pick):
    # Mock the return value of pick to simulate user selection
    expected_instance = ("i-1234567890abcdef0", "my-instance", "192.168.1.1", "2021-06-01 12:00:00")
    mock_pick.return_value = [expected_instance]

    # Mock list of instances and title
    instances = [
        ("i-1234567890abcdef0", "my-instance", "192.168.1.1", "2021-06-01 12:00:00"),
        ("i-0987654321fedcba0", "another-instance", "192.168.1.2", "2021-06-01 13:00:00"),
    ]

    title = "Please choose the instance to connect to:"

    # Call the function
    selected_instance = user_pick_instance(instances, title)[0]

    # Assert that the function returns the first element of the tuple returned by pick
    assert selected_instance == expected_instance[0]
    # Assert that pick was called with the correct parameters
    mock_pick.assert_called_once_with(instances, title=title, multiselect=False, min_selection_count=1, indicator="=>")


# Fixture to mock sys.argv for command-line arguments
@pytest.fixture
def mock_sys_argv():
    with patch("sys.argv", ["script_name", "--profile", "dev", "--name", "test-instance", "--region", "eu-west-1"]):
        yield


@patch("ec2_ssh.ec2_ssh.load_conf_file")
@patch("ec2_ssh.cli.create_arg_parser")
def test_main(mock_create_arg_parser, mock_load_conf_file):
    # Arrange
    mock_load_conf_file.return_value = {"username": "test_user", "bastion": "test_bastion"}

    args = MagicMock()
    args.profile = "dev"
    mock_create_arg_parser.return_value.parse_args.return_value = args


def test_user_pick_instance_other():
    # Given: A list of instance tuples (name, hostname, IP)
    instances = [
        ("Instance A", "hostA", "192.168.1.1"),
        ("Instance B", "hostB", "192.168.1.2"),
        ("Instance C", "hostC", "192.168.1.3"),
    ]

    with patch("ec2_ssh.cli.pick", return_value=(("Instance B", "hostB", "192.168.1.2"), 1)) as mock_pick:
        # When: The user picks an instance
        selected_instance = user_pick_instance(instances, "Please choose the instance to connect to:")

        # Extract host name and IP
        select_host_name = selected_instance[1]
        select_host_ip = selected_instance[2]

        # Then: The selected instance should be the second one
        assert select_host_name == "hostB"
        assert select_host_ip == "192.168.1.2"

        mock_pick.assert_called_once_with(
            instances,
            title="Please choose the instance to connect to:",
            multiselect=False,
            min_selection_count=1,
            indicator="=>",
        )


# Here, replace 'method_or_function' with the actual method or function that's expecting a string or bytes-like object
# @patch('ec2_ssh.ec2_ssh.list_ec2_instances')
# def test_method_or_function(mock_list_ec2_instances):
#     mock_list_ec2_instances.return_value = 'dev'

#     # Act
#     try:
#         result = main()
#     except SystemExit:
#         pass

#     # Assert
#     mock_list_ec2_instances.assert_called_once()

# @patch('ec2_ssh.ec2_ssh.load_conf_file')
# @patch('ec2_ssh.cli.create_arg_parser')
# def test_main(mock_create_arg_parser, mock_load_conf_file, mock_sys_argv):
#     # Arrange
#     mock_load_conf_file.return_value = {
#         "username": "test_user",
#         "bastion": "test_bastion"
#     }

#     args = MagicMock()
#     args.profile = 'dev'
#     mock_create_arg_parser.return_value.parse_args.return_value = args

#     # Act
#     try:
#         result = main()
#     except SystemExit:
#         pass

#     # Assert
#     mock_load_conf_file.assert_called_once()

# @patch('ec2_ssh.cli.sys.exit')
# @patch('ec2_ssh.ec2_ssh.connect_to_ssh_server')
# @patch('ec2_ssh.cli.user_pick_instance')
# @patch('ec2_ssh.ec2_ssh.list_ec2_instances')
# @patch('ec2_ssh.ec2_ssh.load_conf_file')
# @patch('ec2_ssh.cli.create_arg_parser')
# def test_main(mock_create_arg_parser, mock_load_conf_file, mock_list_ec2_instances, mock_user_pick_instance, mock_connect_to_ssh_server, mock_sys_exit):
#     # Arrange
#     mock_args = MagicMock()
#     mock_args.profile = 'test_profile'
#     mock_args.name = 'test_name'
#     mock_args.region = 'test_region'
#     mock_create_arg_parser.return_value.parse_args.return_value = mock_args

#     mock_config = {'username': 'test_username', 'bastion': 'test_bastion'}
#     mock_load_conf_file.return_value = mock_config

#     mock_instances = [('i-1234567890abcdef0', 'my-instance', '192.168.1.1', '2021-06-01 12:00:00')]
#     mock_list_ec2_instances.return_value = mock_instances

#     mock_user_pick_instance.return_value = mock_instances[0]

#     # Act
#     try:
#         result = main()
#     except SystemExit:
#         pass

#     # Assert
#     mock_create_arg_parser.assert_called_once()
#     mock_load_conf_file.assert_called_once()
#     mock_list_ec2_instances.assert_called_once_with(mock_args.profile, name_prefix=mock_args.name, region_name=mock_args.region)
#     mock_user_pick_instance.assert_called_once_with(mock_instances, "Please choose the instance to connect to:")
#     mock_connect_to_ssh_server.assert_called_once_with(mock_config['bastion'], mock_config['username'], mock_args.profile, mock_instances[0][1], mock_instances[0][2])
#     assert result == 0
