"""Simple Tkinter GUI for Tomodachi."""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional

from .pet import Pet

TICK_MS = 5000  # 5 seconds per tick for demo


class TomodachiGUI:
    def __init__(self, root: tk.Tk, pet: Optional[Pet] = None) -> None:
        self.root = root
        self.pet = pet or Pet()
        root.title("Tomodachi — Pet Cat")

        self.canvas = tk.Canvas(root, width=300, height=220, bg="#f7f3e9")
        self.canvas.pack(padx=8, pady=8)

        self.status_var = tk.StringVar()
        self._update_status()
        tk.Label(root, textvariable=self.status_var).pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Feed", command=self.feed).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Play", command=self.play).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Sleep", command=self.sleep).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Save", command=self.save).grid(row=0, column=3, padx=4)
        tk.Button(btn_frame, text="Load", command=self.load).grid(row=0, column=4, padx=4)
        tk.Button(btn_frame, text="Quit", command=self.quit).grid(row=0, column=5, padx=4)

        self._draw_pet()
        self._schedule_tick()

    def _draw_pet(self) -> None:
        """Draw a black-and-white 8-bit style sprite scaled onto the canvas.

        Sprites: idle, eating, playing, sleeping, dead
        """
        self.canvas.delete("all")
        sprite_name = self._get_sprite_for_state()
        self._draw_sprite(sprite_name)

    def _update_status(self) -> None:
        self.status_var.set(self.pet.status())

    def feed(self) -> None:
        if not self.pet.alive:
            messagebox.showinfo("No effect", f"{self.pet.name} is no longer alive.")
            return
        self.pet.feed(30)
        self._update_and_redraw()

    def play(self) -> None:
        if not self.pet.alive:
            messagebox.showinfo("No effect", f"{self.pet.name} is no longer alive.")
            return
        ok = self.pet.play(15)
        if not ok:
            messagebox.showinfo("Too tired", f"{self.pet.name} is too tired to play.")
        self._update_and_redraw()

    def sleep(self) -> None:
        if not self.pet.alive:
            messagebox.showinfo("No effect", f"{self.pet.name} is no longer alive.")
            return
        self.pet.sleep(3)
        self._update_and_redraw()

    def save(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            try:
                self.pet.save(path)
                messagebox.showinfo("Saved", f"Saved pet to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def load(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                new = Pet.load(path)
                self.pet = new
                self._update_and_redraw()
                messagebox.showinfo("Loaded", f"Loaded pet from {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")

    def quit(self) -> None:
        self.root.quit()

    def _update_and_redraw(self) -> None:
        self._update_status()
        self._draw_pet()

    def _tick(self) -> None:
        self.pet.tick(TICK_MS // 1000)
        self._update_and_redraw()
        self._schedule_tick()

    def _schedule_tick(self) -> None:
        self.root.after(TICK_MS, self._tick)

    # sprite selection and drawing helpers as class methods (avoid dynamic assignment)
    def _get_sprite_for_state(self) -> str:
        if not self.pet.alive:
            return "dead"
        if self.pet.energy < 20:
            return "sleeping"
        if self.pet.hunger < 30:
            return "eating"
        if self.pet.happiness > 65:
            return "playing"
        return "idle"

    def _draw_sprite(self, sprite_name: str) -> None:
        sprite = SPRITES.get(sprite_name, SPRITES["idle"])
        self._draw_sprite_on_canvas(sprite)

    def _draw_sprite_on_canvas(self, sprite: list[list[int]], x_offset: int = 40, y_offset: int = 20) -> None:
        for y, row in enumerate(sprite):
            for x, v in enumerate(row):
                if v:
                    x1 = x_offset + x * PIXEL_SCALE
                    y1 = y_offset + y * PIXEL_SCALE
                    x2 = x_offset + (x + 1) * PIXEL_SCALE
                    y2 = y_offset + (y + 1) * PIXEL_SCALE
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")


def run_gui() -> None:
    root = tk.Tk()
    app = TomodachiGUI(root)
    root.mainloop()

    
### 8-bit sprite helpers
PIXEL_SCALE = 6

# Sprites are small 8x8 monochrome matrices (1 = black, 0 = white)
SPRITES = {
    "idle": [
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,0,1,1,0,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,0,0,1,0,0],
        [0,0,0,1,1,0,0,0],
    ],
    "eating": [
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,0,1,1,0,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,0,1,0,0],
        [0,0,0,1,1,0,0,0],
    ],
    "playing": [
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,0,1,1,0,1,1],
        [1,1,1,0,0,1,1,1],
        [1,1,0,1,1,0,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,0,0,1,0,0],
        [0,1,0,0,0,0,1,0],
    ],
    "sleeping": [
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,0,1,1,0,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0],
    ],
    "dead": [
        [0,0,1,1,1,1,0,0],
        [0,1,1,0,0,1,1,0],
        [1,1,0,0,0,0,1,1],
        [1,1,0,0,0,0,1,1],
        [1,1,0,0,0,0,1,1],
        [0,1,1,0,0,1,1,0],
        [0,0,1,1,1,1,0,0],
        [0,0,0,0,0,0,0,0],
    ],
}


def _scaled_rect_coords(x: int, y: int) -> tuple[int, int, int, int]:
    sx = x * PIXEL_SCALE
    sy = y * PIXEL_SCALE
    return (sx, sy, sx + PIXEL_SCALE, sy + PIXEL_SCALE)


def _draw_sprite_on_canvas(canvas: tk.Canvas, sprite: list[list[int]], x_offset: int = 40, y_offset: int = 20) -> None:
    for y, row in enumerate(sprite):
        for x, v in enumerate(row):
            if v:
                x1, y1, x2, y2 = (x_offset + x * PIXEL_SCALE, y_offset + y * PIXEL_SCALE,
                                  x_offset + (x + 1) * PIXEL_SCALE, y_offset + (y + 1) * PIXEL_SCALE)
                canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")


def _choose_sprite_for_pet(pet: Pet) -> str:
    if not pet.alive:
        return "dead"
    # choose sprite by energy/happiness and recent action
    if pet.energy < 20:
        return "sleeping"
    if pet.hunger < 30:
        return "eating"
    if pet.happiness > 65:
        return "playing"
    return "idle"


def _draw_sprite(self: TomodachiGUI, sprite_name: str) -> None:
    sprite = SPRITES.get(sprite_name, SPRITES["idle"])
    _draw_sprite_on_canvas(self.canvas, sprite)


# (helpers are implemented as class methods above)

