import paramiko

class SFTPUploader:
    def __init__(self, host, username, password,port=22):
        """
        Initializes the SFTPUploader with connection details.

        :param host: SFTP server address
        :param port: SFTP server port (usually 22)
        :param username: Username for SFTP authentication
        :param password: Password for SFTP authentication
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = None
        self.sftp_client = None

    def connect(self):
        """
        Establishes the SSH and SFTP connection.
        """
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(
                hostname=self.host, port=self.port, username=self.username, password=self.password
            )
            self.sftp_client = self.ssh_client.open_sftp()
        except Exception as e:
            self.disconnect()
            raise ConnectionError(f"Failed to connect to SFTP server: {e}")

    def upload_csv(self, csv_data_io, remote_path):
        """
        Uploads a CSV file to the specified remote path on the SFTP server.

        :param csv_data_io: StringIO object containing the CSV data to upload
        :param remote_path: Remote path on the server where the CSV file will be saved
        """
        if not self.sftp_client:
            raise ConnectionError("SFTP client is not connected.")

        try:
            with self.sftp_client.file(remote_path, 'w') as remote_file:
                remote_file.write(csv_data_io.getvalue())
            print("CSV file uploaded successfully!")
        except Exception as e:
            raise IOError(f"Failed to upload CSV file: {e}")

    def disconnect(self):
        """
        Closes the SFTP and SSH connections.
        """
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
