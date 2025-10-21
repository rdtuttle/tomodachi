"""Entry point: prefer GUI when available, otherwise CLI. Web version available."""
import sys

try:
    from .gui import run_gui  # type: ignore
except Exception:
    run_gui = None  # GUI not available

try:
    from .web import run_web  # type: ignore
except Exception:
    run_web = None  # Web interface not available

from .cli import main as run_cli


def main() -> None:
    # Check for --web flag
    if '--web' in sys.argv:
        if run_web:
            run_web()
            return
        print("Web interface not available. Install flask to use web interface.")
        sys.exit(1)
        
    # Otherwise try GUI, then CLI
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
