"""Entry point: prefer GUI when available, otherwise CLI."""
try:
    from .gui import run_gui  # type: ignore
except Exception:
    run_gui = None  # GUI not available

from .cli import main as run_cli


def main() -> None:
    if run_gui:
        try:
            run_gui()
            return
        except Exception:
            # fall back to CLI
            pass
    run_cli()


if __name__ == "__main__":
    main()
