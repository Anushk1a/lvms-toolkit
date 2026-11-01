import json

from typer.testing import CliRunner

from lvms_toolkit.cli import app
from lvms_toolkit.preflight import index_devices, inspect_device

runner = CliRunner()

CLEAN = {
    "blockdevices": [
        {
            "name": "/dev/sdb",
            "type": "disk",
            "size": 10737418240,
            "fstype": None,
            "mountpoints": [None],
        }
    ]
}

MOUNTED = {
    "blockdevices": [
        {
            "name": "/dev/sdb",
            "type": "disk",
            "size": 10737418240,
            "fstype": None,
            "mountpoints": ["/data"],
        }
    ]
}


def test_clean_disk_is_safe():
    assert inspect_device("/dev/sdb", index_devices(CLEAN)) == []


def test_missing_device_is_flagged():
    findings = inspect_device("/dev/sdz", index_devices(CLEAN))
    assert findings[0].message == "device not found"


def test_plan_passes_on_clean_disk(tmp_path):
    snapshot = tmp_path / "lsblk.json"
    snapshot.write_text(json.dumps(CLEAN))
    result = runner.invoke(
        app, ["plan", "spec/examples/single-node.yaml", "--lsblk-json", str(snapshot)]
    )
    assert result.exit_code == 0


def test_plan_blocks_mounted_disk(tmp_path):
    snapshot = tmp_path / "lsblk.json"
    snapshot.write_text(json.dumps(MOUNTED))
    result = runner.invoke(
        app, ["plan", "spec/examples/single-node.yaml", "--lsblk-json", str(snapshot)]
    )
    assert result.exit_code == 1
    assert "mounted" in result.output