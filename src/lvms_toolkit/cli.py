import json
import subprocess

import typer
import yaml
from pydantic import ValidationError

from lvms_toolkit.preflight import check_spec, read_lsblk
from lvms_toolkit.render import render_lvmcluster, to_yaml
from lvms_toolkit.schema import Spec, load_spec

app = typer.Typer(help="LVMS storage automation toolkit")


def _load_or_exit(path: str) -> Spec:
    try:
        return load_spec(path)
    except FileNotFoundError:
        typer.secho(f"error: file not found: {path}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)
    except yaml.YAMLError as exc:
        typer.secho(f"error: not valid YAML: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)
    except ValidationError as exc:
        typer.secho(f"{path}: invalid spec", fg=typer.colors.RED, err=True)
        for err in exc.errors():
            location = ".".join(str(p) for p in err["loc"]) or "(root)"
            typer.echo(f"  - {location}: {err['msg']}", err=True)
        raise typer.Exit(code=1)


@app.callback()
def main() -> None:
    """LVMS storage automation toolkit."""


@app.command()
def validate(
    path: str = typer.Argument(..., help="Path to the spec YAML file"),
) -> None:
    """Check a spec file and report every problem found."""
    spec = _load_or_exit(path)
    count = len(spec.device_classes)
    typer.secho(f"{path}: OK ({count} device class(es))", fg=typer.colors.GREEN)


@app.command()
def render(
    path: str = typer.Argument(..., help="Path to the spec YAML file"),
) -> None:
    """Print the LVMCluster manifest for a spec."""
    spec = _load_or_exit(path)
    typer.echo(to_yaml(render_lvmcluster(spec)), nl=False)
@app.command()
def plan(
    path: str = typer.Argument(..., help="Path to the spec YAML file"),
    lsblk_json: str | None = typer.Option(
        None,
        "--lsblk-json",
        help="Read disk info from a saved lsblk JSON file instead of this machine",
    ),
) -> None:
    """Check that every device in the spec is safe to use. Changes nothing."""
    spec = _load_or_exit(path)
    try:
        if lsblk_json:
            with open(lsblk_json) as f:
                lsblk = json.load(f)
        else:
            lsblk = read_lsblk()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        typer.secho(
            f"error: could not read disk information: {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=2)

    findings = check_spec(spec, lsblk)
    if findings:
        typer.secho("plan: NOT SAFE to apply", fg=typer.colors.RED, err=True)
        for finding in findings:
            typer.echo(f"  - {finding.device}: {finding.message}", err=True)
        raise typer.Exit(code=1)

    typer.secho("plan: all devices look safe to use", fg=typer.colors.GREEN)    