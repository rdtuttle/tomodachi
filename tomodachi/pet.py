"""Simple Tomodachi Pet model with care tracking and real-time death."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def _clamp(v: int) -> int:
    return max(0, min(100, int(v)))


@dataclass
class Pet:
    name: str = "Tomo"
    hunger: int = 50
    happiness: int = 50
    energy: int = 50
    alive: bool = True
    # cumulative real seconds spent playing (keeps activity history)
    cumulative_play_seconds: int = 0
    # care score (0-100). Higher means better care and longer allowed neglect.
    care_score: int = 50
    # ISO timestamp when the pet was last cared for (feed/play/sleep)
    last_cared: Optional[str] = None

    def status(self) -> str:
        alive_text = "alive" if self.alive else "dead"
        return (
            f"{self.name} ({alive_text}) — Hunger: {self.hunger}/100, Happiness: {self.happiness}/100, "
            f"Energy: {self.energy}/100, Care: {self.care_score}/100"
        )

    def feed(self, amount: int = 20) -> None:
        """Feed the pet: reduces hunger and slightly increases happiness."""
        if not self.alive:
            return
        self.hunger = _clamp(self.hunger - amount)
        self.happiness = _clamp(self.happiness + 5)
        self._on_cared(amount=3)

    def play(self, minutes: int = 10) -> bool:
        """Play with the pet. Returns False if the pet is too tired."""
        if not self.alive:
            return False
        cost = max(1, minutes // 2)
        if self.energy < cost:
            return False
        self.happiness = _clamp(self.happiness + minutes // 2)
        self.energy = _clamp(self.energy - cost)
        self.hunger = _clamp(self.hunger + minutes // 3)
        # accumulate real play time and update care
        self.add_play_seconds(minutes * 60)
        self._on_cared(amount=2)
        return True

    def add_play_seconds(self, seconds: int) -> None:
        """Increment cumulative play seconds; real-time death is handled separately."""
        if not self.alive:
            return
        self.cumulative_play_seconds += int(seconds)

    def sleep(self, hours: int = 2) -> None:
        """Pet sleeps and regains energy but gets a bit hungrier."""
        if not self.alive:
            return
        self.energy = _clamp(self.energy + hours * 25)
        self.hunger = _clamp(self.hunger + hours * 5)
        # sleeping counts as care
        self._on_cared(amount=1)

    def tick(self, minutes: int = 60) -> None:
        """Progress time: hunger increases, happiness and energy decrease."""
        if not self.alive:
            return
        hours = max(1, minutes // 60)
        self.hunger = _clamp(self.hunger + 5 * hours)
        self.happiness = _clamp(self.happiness - 2 * hours)
        self.energy = _clamp(self.energy - 5 * hours)

    def _on_cared(self, amount: int = 1) -> None:
        """Called when user performs a caring action. Increases care_score and updates last_cared timestamp."""
        if not self.alive:
            return
        self.care_score = _clamp(self.care_score + amount)
        self.update_last_cared()
        self.check_alive()

    def update_last_cared(self, when: Optional[datetime] = None) -> None:
        now = when or datetime.now(timezone.utc)
        self.last_cared = now.isoformat()

    def compute_death_threshold_days(self) -> float:
        """Compute allowed neglect days from care_score.

        care_score 0 -> 3 days
        care_score 100 -> 30 days
        Linear interpolation between.
        """
        return 3.0 + (float(self.care_score) / 100.0) * 27.0

    def check_alive(self) -> None:
        """Update the `alive` flag based on last_cared and care threshold."""
        if not self.alive:
            return
        if not self.last_cared:
            # if never cared for, treat creation time as last cared
            self.update_last_cared()
            return
        try:
            last = datetime.fromisoformat(self.last_cared)
            now = datetime.now(timezone.utc)
            elapsed = now - last
            threshold_days = self.compute_death_threshold_days()
            if elapsed.total_seconds() >= threshold_days * 24 * 3600:
                self.alive = False
        except Exception:
            # if parsing fails, be conservative and keep alive
            pass

    def to_dict(self) -> dict:
        data = asdict(self)
        # ensure last_cared is serializable string or None
        if isinstance(self.last_cared, datetime):
            data["last_cared"] = self.last_cared.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        # support older save files by providing defaults
        kwargs = {
            "name": data.get("name", "Tomo"),
            "hunger": int(data.get("hunger", 50)),
            "happiness": int(data.get("happiness", 50)),
            "energy": int(data.get("energy", 50)),
            "alive": bool(data.get("alive", True)),
            "cumulative_play_seconds": int(data.get("cumulative_play_seconds", 0)),
            "care_score": int(data.get("care_score", 50)),
            "last_cared": data.get("last_cared", None),
        }
        pet = cls(**kwargs)
        pet.check_alive()
        return pet

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Pet":
        p = Path(path)
        data = json.loads(p.read_text())
        return cls.from_dict(data)
