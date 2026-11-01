import json
import subprocess
from dataclasses import dataclass

from lvms_toolkit.schema import Spec

# loop devices are allowed so the same checks work in CI, where disks are loop-backed files
ALLOWED_TYPES = {"disk", "loop"}


@dataclass
class Finding:
    device: str
    message: str


def read_lsblk() -> dict:
    result = subprocess.run(
        ["lsblk", "-J", "-p", "-b", "-o", "NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def index_devices(lsblk: dict) -> dict[str, dict]:
    return {d["name"]: d for d in lsblk.get("blockdevices", [])}


def inspect_device(path: str, devices: dict[str, dict]) -> list[Finding]:
    dev = devices.get(path)
    if dev is None:
        return [Finding(path, "device not found")]

    findings = []
    if dev.get("type") not in ALLOWED_TYPES:
        findings.append(Finding(path, f"not a whole disk (type: {dev.get('type')})"))
    if dev.get("fstype"):
        findings.append(Finding(path, f"has an existing {dev['fstype']} signature"))
    if any(dev.get("mountpoints") or []):
        findings.append(Finding(path, "is mounted or in use"))
    if dev.get("children"):
        findings.append(Finding(path, "has partitions or volumes on it"))
    return findings


def check_spec(spec: Spec, lsblk: dict) -> list[Finding]:
    devices = index_devices(lsblk)
    findings = []
    for dc in spec.device_classes:
        for path in dc.devices:
            findings.extend(inspect_device(path, devices))
    return findings
