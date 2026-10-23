"""Anonymous access to public S3 buckets."""

import asyncio
from pathlib import Path

import obstore
from obstore.store import S3Store


def make_store(bucket: str, region: str) -> S3Store:
    """Create an unsigned store for a public bucket."""
    return S3Store(
        bucket,
        region=region,
        skip_signature=True,
        virtual_hosted_style_request=False,
    )


def list_keys(store: S3Store, prefix: str) -> list[str]:
    """List all object keys under ``prefix``."""
    return [meta["path"] for batch in obstore.list(store, prefix) for meta in batch]


def read(store: S3Store, key: str) -> bytes:
    """Read a single object."""
    return bytes(obstore.get(store, key).bytes())


def download(
    store: S3Store, keys_to_paths: dict[str, Path], max_concurrency: int = 16
) -> None:
    """Download objects to local paths concurrently."""

    async def _download_all() -> None:
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _download_one(key: str, path: Path) -> None:
            async with semaphore:
                response = await obstore.get_async(store, key)
                content = await response.bytes_async()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bytes(content))

        await asyncio.gather(
            *(_download_one(key, path) for key, path in keys_to_paths.items())
        )

    asyncio.run(_download_all())
