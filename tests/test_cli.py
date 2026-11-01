import yaml
from typer.testing import CliRunner

from lvms_toolkit.cli import app

runner = CliRunner()


def test_validate_ok():
    result = runner.invoke(app, ["validate", "spec/examples/single-node.yaml"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_validate_missing_file():
    result = runner.invoke(app, ["validate", "does-not-exist.yaml"])
    assert result.exit_code == 2


def test_validate_invalid_spec(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "apiVersion: toolkit/v1\n"
        "cluster:\n  name: lab\n"
        "deviceClasses:\n"
        "  - name: fast\n"
        "    devices: [sdb]\n"
        "    thinPool:\n      name: tp\n"
    )
    result = runner.invoke(app, ["validate", str(bad)])
    assert result.exit_code == 1
    assert "/dev/" in result.output

def test_render_outputs_valid_yaml():
    result = runner.invoke(app, ["render", "spec/examples/single-node.yaml"])
    assert result.exit_code == 0
    assert yaml.safe_load(result.output)["kind"] == "LVMCluster"    