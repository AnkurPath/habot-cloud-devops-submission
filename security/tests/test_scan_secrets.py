from pathlib import Path

from scan_secrets import scan_file


def test_scan_file_rejects_high_entropy_api_key(tmp_path: Path) -> None:
    source = tmp_path / "settings.py"
    demo_value = "abc1234567890" + "XYZTOKENVALUE"
    source.write_text(f'API_KEY = "{demo_value}"\n', encoding="utf-8")

    findings = scan_file(source, tmp_path)

    assert len(findings) == 1
    assert findings[0].rule == "hardcoded-secret-assignment"


def test_scan_file_allows_environment_reference(tmp_path: Path) -> None:
    source = tmp_path / "settings.py"
    source.write_text('API_KEY = os.environ["API_KEY"]\n', encoding="utf-8")

    findings = scan_file(source, tmp_path)

    assert findings == []
