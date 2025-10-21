"""Command-line helpers for Tomodachi."""
from __future__ import annotations

from pathlib import Path
from .pet import Pet
from typing import Tuple


def status(pet: Pet) -> str:
    return pet.status()


def handle_command(pet: Pet, command: str) -> Tuple[bool, str]:
    """Handle a single command.
    Returns (should_quit, message)
    """
    parts = command.strip().split()
    if not parts:
        return False, ""
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "status":
        return False, status(pet)
    if cmd == "feed":
        amt = int(args[0]) if args else 20
        pet.feed(amt)
        return False, f"You fed {pet.name}."
    if cmd == "play":
        mins = int(args[0]) if args else 10
        ok = pet.play(mins)
        return False, ("You played with your pet." if ok else "Pet is too tired to play.")
    if cmd == "sleep":
        hrs = int(args[0]) if args else 2
        pet.sleep(hrs)
        return False, f"{pet.name} slept for {hrs} hours."
    if cmd == "save":
        path = args[0] if args else "pet.json"
        pet.save(path)
        return False, f"Saved to {path}"
    if cmd == "load":
        path = args[0] if args else "pet.json"
        try:
            new = Pet.load(path)
            pet.name = new.name
            pet.hunger = new.hunger
            pet.happiness = new.happiness
            pet.energy = new.energy
            return False, f"Loaded from {path}"
        except Exception as e:
            return False, f"Failed to load: {e}"
    if cmd in ("quit", "exit"):
        return True, "Goodbye!"
    return False, "Unknown command."


def main() -> None:
    pet = Pet()
    print("Welcome to Tomodachi! Type 'status' to see your pet. 'quit' to exit.")
    while True:
        try:
            cmd = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        quit_flag, msg = handle_command(pet, cmd)
        if msg:
            print(msg)
        if quit_flag:
            break
