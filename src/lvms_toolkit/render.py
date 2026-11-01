import yaml

from lvms_toolkit.schema import DeviceClass, Spec

API_VERSION = "lvm.topolvm.io/v1alpha1"
NAMESPACE = "openshift-storage"


def render_device_class(dc: DeviceClass) -> dict:
    return {
        "name": dc.name,
        "default": dc.default,
        "fstype": dc.fs_type,
        "deviceSelector": {"paths": list(dc.devices)},
        "thinPoolConfig": {
            "name": dc.thin_pool.name,
            "sizePercent": dc.thin_pool.size_percent,
            "overprovisionRatio": dc.thin_pool.overprovision_ratio,
        },
    }


def render_lvmcluster(spec: Spec) -> dict:
    return {
        "apiVersion": API_VERSION,
        "kind": "LVMCluster",
        "metadata": {"name": spec.cluster.name, "namespace": NAMESPACE},
        "spec": {
            "storage": {
                "deviceClasses": [render_device_class(dc) for dc in spec.device_classes]
            }
        },
    }


def to_yaml(manifest: dict) -> str:
    return yaml.safe_dump(manifest, sort_keys=False)