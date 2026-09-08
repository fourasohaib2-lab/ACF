from pathlib import Path

from acf.utils.files import ensure_directory


def test_create_directory(tmp_path):
    directory = tmp_path / "demo"
    ensure_directory(directory)
    assert Path(directory).exists()
