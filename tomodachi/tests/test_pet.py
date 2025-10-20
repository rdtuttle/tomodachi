import os
import sys
import json
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tomodachi.pet import Pet


def test_feed_play_sleep_and_save_load(tmp_path):
    pet = Pet(name="Test", hunger=60, happiness=40, energy=30)
    pet.feed(30)
    assert pet.hunger <= 40
    pet.play(10)
    assert pet.happiness >= 40
    pet.sleep(1)
    assert pet.energy >= 30

    p = tmp_path / "pet.json"
    pet.save(p)
    loaded = Pet.load(p)
    assert loaded.name == pet.name
    assert loaded.hunger == pet.hunger
    assert loaded.happiness == pet.happiness
    assert loaded.energy == pet.energy
