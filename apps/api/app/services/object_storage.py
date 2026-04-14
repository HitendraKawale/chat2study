from __future__ import annotations

from pathlib import Path

import boto3
from botocore.client import Config

from app.core.config import settings


class ObjectStorageService:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.aws_default_region,
            config=Config(
                s3={"addressing_style": "path" if settings.s3_force_path_style else "auto"}
            ),
        )
        self.bucket = settings.s3_bucket

    def upload_file(self, local_path: Path, object_key: str, content_type: str) -> str:
        with local_path.open("rb") as f:
            self.client.upload_fileobj(
                f,
                self.bucket,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )
        return object_key
