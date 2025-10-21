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
        # Modern color palette
        self.COLORS = {
            'bg': '#1a1c2c',        # Dark background
            'primary': '#5d275d',    # Purple
            'secondary': '#b13e53',  # Red
            'accent': '#38b764',     # Green
            'text': '#f4f4f4',       # Light text
            'pet': '#ffcd75',        # Pet color (warm yellow)
            'detail': '#29366f',     # Dark blue details
        }
        
        self.root = root
        self.pet = pet or Pet()
        root.title("Tomodachi — Pet Cat")
        root.configure(bg=self.COLORS['bg'])

        # Main canvas with modern dark theme
        self.canvas = tk.Canvas(root, width=400, height=300, bg=self.COLORS['bg'],
                              highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # Status bars frame
        stats_frame = tk.Frame(root, bg=self.COLORS['bg'])
        stats_frame.pack(pady=10, padx=20, fill='x')

        # Create modern stat bars
        self.hunger_bar = tk.Canvas(stats_frame, width=100, height=10, bg=self.COLORS['detail'],
                                  highlightthickness=0)
        self.happiness_bar = tk.Canvas(stats_frame, width=100, height=10, bg=self.COLORS['detail'],
                                     highlightthickness=0)
        self.energy_bar = tk.Canvas(stats_frame, width=100, height=10, bg=self.COLORS['detail'],
                                  highlightthickness=0)

        # Labels for stats with modern font
        tk.Label(stats_frame, text="Hunger", fg=self.COLORS['text'], bg=self.COLORS['bg'],
                font=('Helvetica', 10)).grid(row=0, column=0, padx=5)
        self.hunger_bar.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(stats_frame, text="Happiness", fg=self.COLORS['text'], bg=self.COLORS['bg'],
                font=('Helvetica', 10)).grid(row=1, column=0, padx=5)
        self.happiness_bar.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(stats_frame, text="Energy", fg=self.COLORS['text'], bg=self.COLORS['bg'],
                font=('Helvetica', 10)).grid(row=2, column=0, padx=5)
        self.energy_bar.grid(row=2, column=1, padx=10, pady=5)

        # Modern button frame
        btn_frame = tk.Frame(root, bg=self.COLORS['bg'])
        btn_frame.pack(pady=15)

        # Modern button style with custom colors and hover effects
        button_style = {
            'font': ('Helvetica', 12),
            'width': 8,
            'bd': 0,
            'padx': 15,
            'pady': 8,
            'relief': 'flat'
        }

        tk.Button(btn_frame, text="Feed", command=self.feed, bg=self.COLORS['primary'],
                 fg=self.COLORS['text'], activebackground=self.COLORS['secondary'],
                 activeforeground=self.COLORS['text'], **button_style).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Play", command=self.play, bg=self.COLORS['primary'],
                 fg=self.COLORS['text'], activebackground=self.COLORS['secondary'],
                 activeforeground=self.COLORS['text'], **button_style).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Sleep", command=self.sleep, bg=self.COLORS['primary'],
                 fg=self.COLORS['text'], activebackground=self.COLORS['secondary'],
                 activeforeground=self.COLORS['text'], **button_style).grid(row=0, column=2, padx=5)
        
        # Second row of buttons
        tk.Button(btn_frame, text="Save", command=self.save, bg=self.COLORS['detail'],
                 fg=self.COLORS['text'], activebackground=self.COLORS['secondary'],
                 activeforeground=self.COLORS['text'], **button_style).grid(row=1, column=0, padx=5, pady=10)
        tk.Button(btn_frame, text="Load", command=self.load, bg=self.COLORS['detail'],
                 fg=self.COLORS['text'], activebackground=self.COLORS['secondary'],
                 activeforeground=self.COLORS['text'], **button_style).grid(row=1, column=1, padx=5, pady=10)
        tk.Button(btn_frame, text="Quit", command=self.quit, bg=self.COLORS['secondary'],
                 fg=self.COLORS['text'], activebackground=self.COLORS['primary'],
                 activeforeground=self.COLORS['text'], **button_style).grid(row=1, column=2, padx=5, pady=10)
        # animation state
        self._anim_frames = []
        self._anim_index = 0
        self._anim_running = False

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
        self.start_animation("eating")
        self._update_and_redraw()

    def play(self) -> None:
        if not self.pet.alive:
            messagebox.showinfo("No effect", f"{self.pet.name} is no longer alive.")
            return
        ok = self.pet.play(15)
        if not ok:
            messagebox.showinfo("Too tired", f"{self.pet.name} is too tired to play.")
        else:
            self.start_animation("playing")
        self._update_and_redraw()

    def sleep(self) -> None:
        if not self.pet.alive:
            messagebox.showinfo("No effect", f"{self.pet.name} is no longer alive.")
            return
        self.pet.sleep(3)
        self.start_animation("sleeping")
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
        self._update_stat_bars()
        self._draw_pet()
        # Schedule next animation frame
        self.root.after(50, self._draw_pet)

    def start_animation(self, name: str, loop: bool = False) -> None:
        """Start animating frames for given action name."""
        frames = ANIMATIONS.get(name)
        if not frames:
            return
        self._anim_frames = frames
        self._anim_index = 0
        self._anim_running = True
        self._anim_progress = 0.0
        self._run_animation_step(loop)

    def _run_animation_step(self, loop: bool) -> None:
        if not self._anim_running:
            return
            
        # Smooth transition between frames
        frame_index = int(self._anim_index)
        next_frame_index = (frame_index + 1) % len(self._anim_frames)
        current_frame = self._anim_frames[frame_index]
        next_frame = self._anim_frames[next_frame_index]
        
        # Clear canvas and draw interpolated frame
        self.canvas.delete("all")
        self._draw_sprite_on_canvas(current_frame)
        
        # Update animation progress
        self._anim_progress += 0.1
        if self._anim_progress >= 1.0:
            self._anim_progress = 0.0
            self._anim_index += 1
            
        if self._anim_index >= len(self._anim_frames):
            if loop:
                self._anim_index = 0
            else:
                self._anim_running = False
                self._update_and_redraw()
                return
                
        # Schedule next frame with smoother timing
        self.root.after(50, lambda: self._run_animation_step(loop))

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

    def _draw_sprite_on_canvas(self, sprite: list[list[int]], x_offset: int = 150, y_offset: int = 100) -> None:
        # Draw a cute background circle
        circle_x = x_offset + 8 * PIXEL_SCALE
        circle_y = y_offset + 8 * PIXEL_SCALE
        radius = 12 * PIXEL_SCALE
        self.canvas.create_oval(
            circle_x - radius, circle_y - radius,
            circle_x + radius, circle_y + radius,
            fill=self.COLORS['detail'], outline="")
        
        # Add a floating animation
        offset_y = int(self._get_float_offset())
        y_offset += offset_y
        
        # Draw the sprite with modern colors
        glow_color = self.COLORS['secondary'] if not self.pet.alive else self.COLORS['accent']
        
        # Draw sprite shadow
        shadow_offset = 4
        for y, row in enumerate(sprite):
            for x, v in enumerate(row):
                if v:
                    x1 = x_offset + x * PIXEL_SCALE
                    y1 = y_offset + y * PIXEL_SCALE + shadow_offset
                    x2 = x_offset + (x + 1) * PIXEL_SCALE
                    y2 = y_offset + (y + 1) * PIXEL_SCALE + shadow_offset
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                              fill=self.COLORS['detail'], outline="")
        
        # Draw the actual sprite
        for y, row in enumerate(sprite):
            for x, v in enumerate(row):
                if v:
                    x1 = x_offset + x * PIXEL_SCALE
                    y1 = y_offset + y * PIXEL_SCALE
                    x2 = x_offset + (x + 1) * PIXEL_SCALE
                    y2 = y_offset + (y + 1) * PIXEL_SCALE
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                              fill=self.COLORS['pet'], outline=glow_color)
                    
    def _get_float_offset(self) -> float:
        """Create a gentle floating animation."""
        import math
        t = self.root.tk.call('clock', 'milliseconds') / 1000.0
        return math.sin(t * 2) * 3  # 3 pixel amplitude
        
    def _update_stat_bars(self) -> None:
        """Update the visual stat bars."""
        # Update hunger bar
        self.hunger_bar.delete("all")
        width = self.pet.hunger
        self.hunger_bar.create_rectangle(0, 0, width, 10,
                                       fill=self.COLORS['accent'], outline="")
        
        # Update happiness bar
        self.happiness_bar.delete("all")
        width = self.pet.happiness
        self.happiness_bar.create_rectangle(0, 0, width, 10,
                                          fill=self.COLORS['primary'], outline="")
        
        # Update energy bar
        self.energy_bar.delete("all")
        width = self.pet.energy
        self.energy_bar.create_rectangle(0, 0, width, 10,
                                       fill=self.COLORS['secondary'], outline="")


def run_gui() -> None:
    root = tk.Tk()
    app = TomodachiGUI(root)
    root.mainloop()

    
### 8-bit sprite helpers
PIXEL_SCALE = 8  # scale up 16x16 pixels nicely

# Sprites are 16x16 monochrome matrices (1 = black, 0 = white)
SPRITES = {}

# Simple animations: lists of 16x16 frames (we'll create minimal frames programmatically)
ANIMATIONS = {}

# Helper: generate a base 16x16 cat-like pattern for idle, then create simple variants
def _make_base_cat() -> list[list[int]]:
    # very small stylized 16x16 cat (0/1)
    frame = [[0]*16 for _ in range(16)]
    # head
    for y in range(3,10):
        for x in range(4,12):
            frame[y][x] = 1
    # ears
    frame[3][5] = 1
    frame[2][6] = 1
    frame[3][10] = 1
    frame[2][9] = 1
    # eyes
    frame[5][6] = 0
    frame[5][9] = 0
    # body
    for y in range(10,14):
        for x in range(3,13):
            frame[y][x] = 1
    return frame


# create simple frames
BASE = _make_base_cat()
SPRITES["idle"] = BASE
# eating frame: mouth open (clear a pixel)
eat = [row[:] for row in BASE]
eat[7][8] = 0
SPRITES["eating"] = eat
# playing frame: paw raised (add pixels)
play = [row[:] for row in BASE]
play[11][3] = 1
play[10][3] = 1
SPRITES["playing"] = play
# sleeping frame: eyes closed
sleep = [row[:] for row in BASE]
sleep[5][6] = 1
sleep[5][9] = 1
SPRITES["sleeping"] = sleep
# dead frame: hollow head
dead = [[0]*16 for _ in range(16)]
for y in range(3,10):
    for x in range(4,12):
        dead[y][x] = 1
for x in range(6,10):
    dead[5][x] = 0
SPRITES["dead"] = dead

# Small animations (2 frames each)
ANIMATIONS["eating"] = [SPRITES["idle"], SPRITES["eating"]]
ANIMATIONS["playing"] = [SPRITES["idle"], SPRITES["playing"]]
ANIMATIONS["sleeping"] = [SPRITES["sleeping"], SPRITES["idle"]]



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

