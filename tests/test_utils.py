from acf.utils.files import ensure_directory
from pathlib import Path

def test_create_directory(tmp_path):
    directory = tmp_path / "demo"
    ensure_directory(directory)
    assert Path(directory).exists()
