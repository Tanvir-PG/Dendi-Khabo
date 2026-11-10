# 🎈 The Great Bag Buster! (Polythene Bag Pop Game)

A funny, colorful, cartoon-style **2D animated Pygame arcade game** where a mischievous schoolboy attempts to blow up and burst a polythene plastic bag in the middle of class!

---

## 🎮 Game Concept & Objectives

- **The Scene:** A bright, lively cartoon classroom with a green chalkboard, ticking wall clock, motivational rules poster, and wooden student desk.
- **The Character:** A funny schoolboy in a blue uniform and red tie sitting at his desk with a shiny polythene bag.
- **The Mission:** Hold down the **SPACEBAR** to make the schoolboy puff his cheeks and blow air into the bag.
- **The Climax:** The bag expands, shines, crinkles, and wobbles under intense air pressure until it hits **100%** and **BURSTS** with an explosive **POP!**, scattering plastic shreds across the classroom!
- **Victory:** The schoolboy celebrates with hands raised high and a giant grin while colorful confetti rains down!

---

## ✨ Features & Visual Highlights

- **Dynamic Schoolboy Animations:**
  - *Idle State:* Gentle breathing bob, eyes blinking periodically, subtle smiling expression.
  - *Blowing State:* Head tilts forward, ballooning red puffed-up cheeks, determined squinting eyes, puckered lips gripping the plastic neck.
  - *High Pressure Strain (>75%):* Flustered trembling, comedic sweat droplets flying off his forehead, jittering eyes!
  - *Victory State:* Both arms thrown high into the air in triumph, laughing smile with gleaming teeth, and happy closed eyes.
- **Realistic Yet Cartoon Polythene Bag:**
  - Drawn using alpha-blended transparent surfaces (`pygame.SRCALPHA`).
  - True glossy plastic appearance with curved white shine reflections and delicate crinkle lines.
  - Expands smoothly from a small deflated pocket up to a huge room-filling monster bag.
  - Comedic sinusoidal wobble that turns into intense vibration at high pressure.
- **Bursting FX & Comic Explosions:**
  - Comic-style jagged starburst with a huge stylized **POP!!** banner.
  - 75+ fluttering plastic shrapnel pieces with realistic gravity and rotation physics.
  - Raining victory confetti in vibrant celebration colors.
- **Air Bubbles & Flow Particles:**
  - Real-time stream of air bubbles injected from the boy's mouth directly into the bag.
- **Zero-Dependency Procedural Sound System:**
  - Custom synthesized sound effects (air blowing breath, comical bursting pop, and victory chime) generated on startup via Python's standard `wave` module—no external `.mp3` or `.wav` downloads required!
- **Classroom Scenery:**
  - Blackboard with chalk doodles, formulas ($P = F / A$), and funny stick figures.
  - Working classroom wall clock with animated ticking hands.
  - Wooden desk with pencil cup, stationery, and stacked textbooks.

---

## 🕹️ Controls

| Key / Action | Function |
| :--- | :--- |
| **HOLD [SPACEBAR]** | Take a deep breath and blow air into the polythene bag |
| **RELEASE [SPACEBAR]** | Catch your breath (air slowly leaks out) |
| **[R]** | Restart game at any time |
| **[M]** | Mute / Unmute Sound Effects |
| **[ESC]** | Quit game |
| **Left Click "PLAY AGAIN"** | Click the interactive button on the victory screen |

---

## 🚀 How to Run the Game

### Method 1: Easy 1-Click Launch (Windows)
Simply double-click the included batch script:
```text
run_game.bat
```
This script automatically checks for Python, installs Pygame if needed, and launches the game immediately.

---

### Method 2: Manual Command Line
1. Open Command Prompt or PowerShell in the project folder:
   ```bash
   cd "C:\Users\Tanvir Ahmed\Desktop\PolytheneBagBurstGame"
   ```
2. Install Pygame:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

---

## 🛠️ Technical Details
- **Language:** Python 3.x
- **Engine:** Pygame
- **Resolution:** 900 × 600 pixels
- **Frame Rate:** Smooth 60 FPS
- **Architecture:** Clean single-file modular design with separated state management, particle systems, procedural sound synthesizer, and drawing pipelines.

