import pytest
from pydantic import ValidationError

from lvms_toolkit.schema import Spec, load_spec


def valid_spec() -> dict:
    return {
        "apiVersion": "toolkit/v1",
        "cluster": {"name": "lab"},
        "deviceClasses": [
            {
                "name": "fast",
                "default": True,
                "devices": ["/dev/sdb"],
                "thinPool": {"name": "thin-pool-1"},
            }
        ],
    }


def test_example_file_loads():
    spec = load_spec("spec/examples/single-node.yaml")
    assert spec.device_classes[0].name == "fast"


def test_defaults_are_applied():
    spec = Spec.model_validate(valid_spec())
    assert spec.device_classes[0].thin_pool.size_percent == 90
    assert spec.device_classes[0].fs_type == "xfs"


def test_bad_device_path_rejected():
    data = valid_spec()
    data["deviceClasses"][0]["devices"] = ["sdb"]
    with pytest.raises(ValidationError, match="must start with /dev/"):
        Spec.model_validate(data)


def test_duplicate_class_names_rejected():
    data = valid_spec()
    second = {**data["deviceClasses"][0], "default": False, "devices": ["/dev/sdc"]}
    data["deviceClasses"].append(second)
    with pytest.raises(ValidationError, match="unique"):
        Spec.model_validate(data)


def test_two_defaults_rejected():
    data = valid_spec()
    data["deviceClasses"].append(
        {
            "name": "slow",
            "default": True,
            "devices": ["/dev/sdc"],
            "thinPool": {"name": "thin-pool-2"},
        }
    )
    with pytest.raises(ValidationError, match="at most one"):
        Spec.model_validate(data)


def test_unknown_field_rejected():
    data = valid_spec()
    data["clusterr"] = {"name": "typo"}
    with pytest.raises(ValidationError):
        Spec.model_validate(data)