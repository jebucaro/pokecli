import json
from pathlib import Path

import pytest

from pokecli.cache.storage import ResilientJSONStorage


def _write(path: Path, text: str) -> None:
    path.write_text(text)


class TestCorruptRead:
    def test_extra_data_is_recovered_as_empty(self, tmp_path, capsys):
        path = tmp_path / "cache.json"
        # valid JSON object followed by trailing bytes, the reported failure
        _write(path, '{"_default": {}}garbage')

        storage = ResilientJSONStorage(str(path))
        assert storage.read() is None
        storage.close()

        backups = list(tmp_path.glob("cache.json.corrupt-*"))
        assert len(backups) == 1
        assert backups[0].read_text() == '{"_default": {}}garbage'
        assert "corrupt" in capsys.readouterr().err

    def test_valid_file_reads_normally_without_backup(self, tmp_path, capsys):
        path = tmp_path / "cache.json"
        _write(path, '{"_default": {"1": {"key": "pikachu"}}}')

        storage = ResilientJSONStorage(str(path))
        assert storage.read() == {"_default": {"1": {"key": "pikachu"}}}
        storage.close()

        assert list(tmp_path.glob("cache.json.corrupt-*")) == []
        assert capsys.readouterr().err == ""

    def test_repeated_reads_back_up_once(self, tmp_path):
        path = tmp_path / "cache.json"
        _write(path, "{}trailing")

        storage = ResilientJSONStorage(str(path))
        assert storage.read() is None
        # a second read now sees the fresh empty file, no new backup
        assert storage.read() is None
        storage.close()

        assert len(list(tmp_path.glob("cache.json.corrupt-*"))) == 1


class TestAtomicWrite:
    def test_write_then_read_round_trips(self, tmp_path):
        path = tmp_path / "cache.json"
        storage = ResilientJSONStorage(str(path), access_mode="r+")
        data = {"_default": {"1": {"key": "pikachu", "data": {"id": 25}}}}
        storage.write(data)
        assert storage.read() == data
        storage.close()

    def test_no_temp_files_left_after_write(self, tmp_path):
        path = tmp_path / "cache.json"
        storage = ResilientJSONStorage(str(path), access_mode="r+")
        storage.write({"_default": {}})
        storage.close()

        leftovers = [p.name for p in tmp_path.iterdir() if p.name != "cache.json"]
        assert leftovers == []

    def test_failed_write_leaves_original_intact(self, tmp_path, monkeypatch):
        path = tmp_path / "cache.json"
        storage = ResilientJSONStorage(str(path), access_mode="r+")
        storage.write({"_default": {"1": {"key": "good"}}})

        def boom(*_args, **_kwargs):
            raise ValueError("cannot serialize")

        monkeypatch.setattr(json, "dumps", boom)
        with pytest.raises(ValueError):
            storage.write({"_default": {"2": {"key": "new"}}})
        storage.close()

        # original content survives and no temp file leaked
        assert json.loads(path.read_text()) == {"_default": {"1": {"key": "good"}}}
        leftovers = [p.name for p in tmp_path.iterdir() if p.name != "cache.json"]
        assert leftovers == []
