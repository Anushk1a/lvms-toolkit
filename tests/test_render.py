from lvms_toolkit.render import render_lvmcluster
from lvms_toolkit.schema import load_spec


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