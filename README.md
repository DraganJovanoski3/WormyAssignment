# Wormy Assignment

A modified version of the classic Snake/Wormy game with additional features for a homework assignment.

## Features

### 1. Second Worm
- A second worm (blue/cyan) appears after 20 seconds
- Random movement AI
- Collision mechanics: head touching body causes growth

### 2. Blinking Items
- **Type 1 (Yellow)**: Appears every 5 seconds, lasts 5 seconds
- **Type 2 (Cyan)**: Appears only once, lasts 7 seconds
- Maximum 3 blinking items on screen at any time
- Eating any blinking item gives +3 points

### 3. Poisonous Apples
- Random 1-5 purple apples spawn between 10-20 seconds
- Stay active for 5 seconds
- Eating one reduces worm length by 2 segments
- Game ends with "You Lost!" if length reaches 0

### 4. Score System
**Formula:**
```
Final Score = Base Score + (Blinking Items Eaten × 3)
```
Where Base Score = Worm Length - 3 (starting length)

## Requirements

- Python 3.x
- Pygame

## Installation

```bash
pip install pygame
```

## Running the Game

```bash
python wormly.py
```

## Controls

- Arrow keys or WASD to move
- ESC to quit

## Screenshots and Videos

See the `media/` folder for screenshots and videos demonstrating each feature.

## Original Code

Based on Wormy by Al Sweigart (al@inventwithpython.com)
Released under a "Simplified BSD" license

