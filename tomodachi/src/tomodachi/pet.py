"""Simple Tomodachi Pet model."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


def _clamp(v: int) -> int:
    return max(0, min(100, int(v)))


@dataclass
class Pet:
    name: str = "Tomo"
    hunger: int = 50
    happiness: int = 50
    energy: int = 50
    alive: bool = True
    # cumulative real seconds spent playing
    cumulative_play_seconds: int = 0
    # days of playing that will cause death when exceeded
    death_threshold_days: int = 3

    def status(self) -> str:
        return (
            f"{self.name} — Hunger: {self.hunger}/100, Happiness: {self.happiness}/100, "
            f"Energy: {self.energy}/100"
        )

    def feed(self, amount: int = 20) -> None:
        """Feed the pet: reduces hunger and slightly increases happiness."""
        self.hunger = _clamp(self.hunger - amount)
        self.happiness = _clamp(self.happiness + 5)

    def play(self, minutes: int = 10) -> bool:
        """Play with the pet. Returns False if the pet is too tired."""
        cost = max(1, minutes // 2)
        if self.energy < cost:
            return False
        self.happiness = _clamp(self.happiness + minutes // 2)
        self.energy = _clamp(self.energy - cost)
        self.hunger = _clamp(self.hunger + minutes // 3)
        # accumulate real play time and check for death
        self.add_play_seconds(minutes * 60)
        return True

    def add_play_seconds(self, seconds: int) -> None:
        """Increment cumulative play seconds and mark pet dead if threshold exceeded."""
        if not self.alive:
            return
        self.cumulative_play_seconds += int(seconds)
        threshold_seconds = int(self.death_threshold_days * 24 * 3600)
        if self.cumulative_play_seconds >= threshold_seconds:
            self.alive = False

    def sleep(self, hours: int = 2) -> None:
        """Pet sleeps and regains energy but gets a bit hungrier."""
        self.energy = _clamp(self.energy + hours * 25)
        self.hunger = _clamp(self.hunger + hours * 5)

    def tick(self, minutes: int = 60) -> None:
        """Progress time: hunger increases, happiness and energy decrease."""
        hours = max(1, minutes // 60)
        self.hunger = _clamp(self.hunger + 5 * hours)
        self.happiness = _clamp(self.happiness - 2 * hours)
        self.energy = _clamp(self.energy - 5 * hours)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        return cls(**{k: data.get(k) for k in ("name", "hunger", "happiness", "energy")})

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Pet":
        p = Path(path)
        data = json.loads(p.read_text())
        return cls.from_dict(data)
