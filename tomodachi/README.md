# Tomodachi — Simple Virtual Pet

A small Python implementation inspired by the original Tomodachi virtual pet toy.

Requirements
- Python 3.10+
- Install dependencies: `pip install -r requirements.txt`

Run

```bash
python -m tomodachi
```

This starts a simple terminal UI. Commands: `status`, `feed`, `play`, `sleep`, `save [path]`, `load [path]`, `quit`.

GUI

If you have Tkinter available (usually included with standard Python on macOS), run:

```bash
export PYTHONPATH=src
python3 -m tomodachi
```

This will launch a small window showing a pet cat and buttons to interact with it.

Tests

```bash
pip install -r requirements.txt
pytest -q tomodachi/tests
```

Files of interest
- `src/tomodachi/pet.py` — core Pet class
- `src/tomodachi/cli.py` — simple CLI and helpers
- `src/tomodachi/__main__.py` — module entrypoint
