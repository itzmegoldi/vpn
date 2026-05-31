import paramiko

from src.pkg import logging

logger = logging.get_logger()


class SSHClient:
    def __init__(self):
        self.client = None

    def connect(self, hostname, username, key_filename):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=hostname, username=username, key_filename=key_filename
            )
            logger.info(f"Connected to {hostname} via SSH")
        except Exception as e:
            logger.error(f"Failed to connect to {hostname} via SSH: {e}")
            raise

    def execute_command(self, command):
        if self.client is None:
            raise Exception("SSH client not connected")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                logger.error(f"Error executing command: {error}")
                raise Exception(error)
            logger.info(f"Command executed successfully: {command}")
            return output
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise

    def close(self):
        if self.client:
            self.client.close()
            logger.info("SSH connection closed")
