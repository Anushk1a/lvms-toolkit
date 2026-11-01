import typer
import yaml
from pydantic import ValidationError

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