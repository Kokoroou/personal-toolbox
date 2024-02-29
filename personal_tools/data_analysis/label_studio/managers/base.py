"""
Base manager for Label Studio
"""
from dataclasses import dataclass

from label_studio_sdk import Client
from paramiko import SSHClient, AutoAddPolicy


@dataclass
class BaseManagerConfig:
    """
    Configuration for BaseManager

    :param url: URL for Label Studio API.
    :param key: API key for Label Studio API.
    :param ip: IP address for remote server of Label Studio.
    :param user: Username for remote server of Label Studio.
    :param password: Password for remote server of Label Studio.
    """
    url: str = ""
    key: str = ""
    ip: str = ""
    user: str = ""
    password: str = ""


class BaseManager:
    """
    Base manager for Label Studio
    """
    def __init__(self, config: BaseManagerConfig):
        """
        Initialize BaseManager class
        """
        if config.url and config.key:
            # Connect to Label Studio by initializing a client
            self.client = Client(url=config.url, api_key=config.key)
            if bool(self.client.check_connection()):
                print("Connected to Label Studio UI.")
            else:
                raise ConnectionError("Failed to connect to Label Studio UI.")

        if config.ip and config.user and config.password:
            # Connect to Label Studio server by SSH
            self.ssh_client = SSHClient()
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh_client.connect(hostname=config.ip,
                                    username=config.user, password=config.password,
                                    timeout=10)
            if bool(self.ssh_client.get_transport().is_active()):
                print("Connected to Label Studio Server.")
            else:
                print("Failed to connect to Label Studio server.")

        print("*" * 50)

    def info(self):
        """
        Print information of Label Studio
        """
        print("Label Studio Info")
        print("Client:", self.client)
        print("SSH Client:", self.ssh_client)

    def __del__(self):
        """
        Close the connection to Label Studio server
        """
        self.ssh_client.close()
