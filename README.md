# Flappy Bird — Computer Graphics Practical Project
## CG Concepts Reference Sheet

---

### PROJECT OVERVIEW
A fully playable Flappy Bird game built in Python using Pygame,
where ALL graphics are rendered using classical Computer Graphics
algorithms implemented from scratch (no pygame.draw for shapes).

---

### CG ALGORITHMS IMPLEMENTED

| # | Algorithm                        | Where Used                        |
|---|----------------------------------|-----------------------------------|
| 1 | Bresenham's Line Drawing         | Pipe edges, beak, texture stripes |
| 2 | Midpoint Circle Generation       | Bird body, eye, pupil, stars      |
| 3 | Midpoint Ellipse Generation      | Clouds, bird wing base            |
| 4 | Scan-Line Polygon Fill           | Pipe body, caps, ground, wing     |
| 5 | Cohen-Sutherland Line Clipping   | Pipe highlight stripes            |
| 6 | 2D Transformations (Rot/Scale)   | Bird tilt/rotation, wing rotation |
| 7 | Double Buffering                 | Frame rendering (flicker-free)    |
| 8 | Parallax Scrolling               | Clouds (slow) vs pipes (fast)     |
| 9 | AABB Collision Detection         | Bird vs pipe hit detection        |

---

### ALGORITHM DETAILS

#### 1. Bresenham's Line Algorithm
- Uses only integer arithmetic
- Decision parameter: err = dx - dy
- If 2*err > -dy: move in x; if 2*err < dx: move in y
- 8-connected pixel placement

#### 2. Midpoint Circle Algorithm
- Decision parameter: p = 1 - r
- Exploits 8-fold symmetry
- If p < 0: p += 2x + 3; else: p += 2(x-y) + 5, y--

#### 3. Midpoint Ellipse Algorithm
- Two-region approach based on slope magnitude
- Region 1: 2*ry²*x < 2*rx²*y
- Region 2: y >= 0

#### 4. Scan-Line Fill Algorithm
- For each horizontal scan line y:
  * Find all edge intersections
  * Sort intersections by x
  * Fill pixel spans between pairs

#### 5. Cohen-Sutherland Clipping
- Assigns 4-bit region code to each endpoint
- LEFT=1, RIGHT=2, BOTTOM=4, TOP=8
- Trivially accept (OR=0), reject (AND≠0), or clip

#### 6. 2D Rotation Transform
- x' = cos(θ)(x-cx) - sin(θ)(y-cy) + cx
- y' = sin(θ)(x-cx) + cos(θ)(y-cy) + cy
- Used for bird tilt and wing rotation

---

### HOW TO RUN
  pip install pygame
  python flappy_bird_cg.py

### CONTROLS
  SPACE / UP / W / Mouse Click — Flap

---
