from typing import Any

import boto3  # type: ignore[import-untyped]

from app.core.config import settings


def _client(endpoint_url: str) -> Any:
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def presigned_upload(
    object_key: str, content_type: str, size_bytes: int, expires: int = 900
) -> str:
    return str(
        _client(settings.s3_public_endpoint).generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": object_key,
                "ContentType": content_type,
                "ContentLength": size_bytes,
            },
            ExpiresIn=expires,
        )
    )


def presigned_download(object_key: str, expires: int = 900) -> str:
    return str(
        _client(settings.s3_public_endpoint).generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": object_key},
            ExpiresIn=expires,
        )
    )


def delete_object(object_key: str) -> None:
    _client(settings.s3_endpoint).delete_object(
        Bucket=settings.s3_bucket,
        Key=object_key,
    )
