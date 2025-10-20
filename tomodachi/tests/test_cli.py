import os
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tomodachi.pet import Pet
from tomodachi.cli import status, handle_command


def test_status_and_commands():
    pet = Pet(name="CliTest", hunger=50, happiness=50, energy=50)
    s = status(pet)
    assert "CliTest" in s

    quit_flag, msg = handle_command(pet, "feed 10")
    assert not quit_flag
    assert "fed" in msg.lower()

    quit_flag, msg = handle_command(pet, "play 5")
    assert not quit_flag

    quit_flag, msg = handle_command(pet, "sleep 1")
    assert not quit_flag

    quit_flag, msg = handle_command(pet, "save test_pet.json")
    assert not quit_flag
    # cleanup
    try:
        Path("test_pet.json").unlink()
    except Exception:
        pass
