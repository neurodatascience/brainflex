from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from pytest_mock import MockerFixture

from brainflex.utils.s3 import download, list_keys, make_store, read


class TestMakeStore:
    def test_make_store(self):
        store = make_store("openneuro.org", "us-east-1")
        assert store.config["bucket"] == "openneuro.org"
        assert store.config["region"] == "us-east-1"
        assert store.config["skip_signature"] == "true"
        assert store.config["virtual_hosted_style_request"] == "false"


class TestListKeys:
    def test_list_keys(self, mocker: MockerFixture):
        mocker.patch(
            "brainflex.utils.s3.obstore.list",
            return_value=[[{"path": "a"}, {"path": "b"}], [{"path": "c"}]],
        )
        assert list_keys(MagicMock(), "prefix/") == ["a", "b", "c"]

    def test_list_keys_empty(self, mocker: MockerFixture):
        mocker.patch("brainflex.utils.s3.obstore.list", return_value=[])
        assert list_keys(MagicMock(), "prefix/") == []


class TestRead:
    def test_read(self, mocker: MockerFixture):
        mock_get = mocker.patch("brainflex.utils.s3.obstore.get")
        mock_get.return_value.bytes.return_value = b"content"
        assert read(MagicMock(), "key") == b"content"


class TestDownload:
    def test_download(self, mocker: MockerFixture, tmp_path: Path):
        async def get_async(store, key):
            response = MagicMock()
            response.bytes_async = AsyncMock(return_value=key.encode())
            return response

        mocker.patch("brainflex.utils.s3.obstore.get_async", side_effect=get_async)
        keys_to_paths = {
            "a": tmp_path / "a.txt",
            "b/c": tmp_path / "b" / "c.txt",
        }
        download(MagicMock(), keys_to_paths)
        assert (tmp_path / "a.txt").read_bytes() == b"a"
        assert (tmp_path / "b" / "c.txt").read_bytes() == b"b/c"
