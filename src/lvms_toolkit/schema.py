from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Base(BaseModel):
    # extra="forbid": a typo like "devicess" is an error, not silently ignored
    # populate_by_name: accept both sizePercent (YAML) and size_percent (Python)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ThinPool(Base):
    name: str
    size_percent: int = Field(default=90, ge=10, le=90, alias="sizePercent")
    overprovision_ratio: int = Field(default=10, ge=1, alias="overprovisionRatio")


class DeviceClass(Base):
    name: str
    default: bool = False
    devices: list[str] = Field(min_length=1)
    thin_pool: ThinPool = Field(alias="thinPool")
    fs_type: Literal["xfs", "ext4"] = Field(default="xfs", alias="fsType")

    @field_validator("devices")
    @classmethod
    def devices_must_be_dev_paths(cls, v: list[str]) -> list[str]:
        for d in v:
            if not d.startswith("/dev/"):
                raise ValueError(f"device path must start with /dev/: {d}")
        return v


class Cluster(Base):
    name: str


class Spec(Base):
    api_version: Literal["toolkit/v1"] = Field(alias="apiVersion")
    cluster: Cluster
    device_classes: list[DeviceClass] = Field(min_length=1, alias="deviceClasses")

    @model_validator(mode="after")
    def cross_checks(self) -> "Spec":
        names = [dc.name for dc in self.device_classes]
        if len(names) != len(set(names)):
            raise ValueError("deviceClass names must be unique")

        if sum(dc.default for dc in self.device_classes) > 1:
            raise ValueError("at most one deviceClass can be default")

        all_devices = [d for dc in self.device_classes for d in dc.devices]
        if len(all_devices) != len(set(all_devices)):
            raise ValueError("a device cannot belong to more than one deviceClass")
        return self


def load_spec(path: str) -> Spec:
    import yaml

    with open(path) as f:
        return Spec.model_validate(yaml.safe_load(f))