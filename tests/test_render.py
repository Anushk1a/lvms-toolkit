from lvms_toolkit.render import render_lvmcluster
from lvms_toolkit.schema import Spec, load_spec


def test_render_single_node():
    spec = load_spec("spec/examples/single-node.yaml")
    manifest = render_lvmcluster(spec)

    assert manifest["kind"] == "LVMCluster"
    dc = manifest["spec"]["storage"]["deviceClasses"][0]
    assert dc["name"] == "fast"
    assert dc["fstype"] == "xfs"
    assert dc["deviceSelector"]["paths"] == ["/dev/sdb"]
    assert dc["thinPoolConfig"]["sizePercent"] == 90


def test_render_never_sets_force_wipe():
    spec = load_spec("spec/examples/single-node.yaml")
    dc = render_lvmcluster(spec)["spec"]["storage"]["deviceClasses"][0]
    assert "forceWipeDevicesAndDestroyAllData" not in dc

def test_render_two_device_classes_in_order():
    spec = Spec.model_validate(
        {
            "apiVersion": "toolkit/v1",
            "cluster": {"name": "lab"},
            "deviceClasses": [
                {
                    "name": "fast",
                    "default": True,
                    "devices": ["/dev/sdb"],
                    "thinPool": {"name": "thin-fast"},
                },
                {
                    "name": "slow",
                    "devices": ["/dev/sdc"],
                    "thinPool": {"name": "thin-slow"},
                },
            ],
        }
    )
    classes = render_lvmcluster(spec)["spec"]["storage"]["deviceClasses"]
    assert len(classes) == 2
    assert [c["name"] for c in classes] == ["fast", "slow"]    