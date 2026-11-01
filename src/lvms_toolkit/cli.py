import typer
import yaml
from pydantic import ValidationError

from lvms_toolkit.schema import load_spec

app = typer.Typer(help="LVMS storage automation toolkit")


@app.callback()
def main() -> None:
    """LVMS storage automation toolkit."""


@app.command()
def validate(
    path: str = typer.Argument(..., help="Path to the spec YAML file"),
) -> None:
    """Check a spec file and report every problem found."""
    try:
        spec = load_spec(path)
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

    count = len(spec.device_classes)
    typer.secho(f"{path}: OK ({count} device class(es))", fg=typer.colors.GREEN)