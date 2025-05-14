import boto3
from botocore.exceptions import ClientError
import json 


class SecretManager():
    def __init__(self):
        self.region_name = "us-east-1"
    
    
    def get_secret_by_secret_key(self,arn,secret_key):
        secret_value = self.get_secret_string(arn)
        return secret_value[secret_key]
    
    
    def get_secret_string(self,arn):
        """
        Retrieves the value of a secret from AWS Secrets Manager.

        Args:
            arn (str): The name of the secret to retrieve.

        Returns:
            str: The secret value retrieved from AWS Secrets Manager, or None if an error occurs.
        """
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )

        try:
            response = client.get_secret_value(
                SecretId=arn
            )
            secret_value = json.loads(response['SecretString'])
            return secret_value
    
        except ClientError as e:
            raise ValueError(f'Error: AwsConn.get_secret:107({e})')