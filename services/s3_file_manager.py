import boto3


class S3FileManager:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, bucket: str):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket = bucket

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    def upload_file(self, file_path: str, s3_key: str):
        self.s3_client.upload_file(file_path, self.bucket, s3_key)

    def upload_empty_file(self, file_key: str) -> None:
        self.s3_client.put_object(Bucket=self.bucket, Key=file_key, Body="")
