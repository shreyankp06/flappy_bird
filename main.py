import pygame
import math
import random
import sys

# ──────────────────────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 480, 640
FPS = 60
GRAVITY = 0.45
FLAP_STRENGTH = -8.5
PIPE_SPEED = 3
PIPE_GAP = 160
PIPE_INTERVAL = 1600   # ms between pipes

# Palette
SKY_TOP    = (100, 181, 246)
SKY_BOT    = (179, 229, 252)
GROUND_COL = (222, 184, 135)
GRASS_COL  = (99,  199,  77)
PIPE_COL   = (56,  142,  60)
PIPE_DARK  = (33,   94,  36)
PIPE_LIGHT = (129, 199, 132)
BIRD_BODY  = (255, 213,  79)
BIRD_WING  = (255, 179,   0)
BIRD_EYE   = (255, 255, 255)
BIRD_PUPIL = (30,   30,  30)
BIRD_BEAK  = (255, 111,   0)
WHITE      = (255, 255, 255)
BLACK      = (0,     0,   0)
RED        = (220,  53,  47)
STAR_COL   = (255, 255, 200)
CLOUD_COL  = (255, 255, 255)
SCORE_COL  = (255, 255, 255)
SHADOW_COL = (0, 0, 0, 120)
GROUND_DARK= (180, 140,  90)


# ══════════════════════════════════════════════════════════════
#  CG ALGORITHM 1 — BRESENHAM'S LINE DRAWING
# ══════════════════════════════════════════════════════════════
def bresenham_line(surface, x0, y0, x1, y1, color, thickness=1):
    """
    Bresenham's Line Algorithm — draws a line using only integer
    arithmetic (no floating point), extremely efficient.
    Decision parameter: d = 2*dy - dx
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if thickness == 1:
            if 0 <= x0 < surface.get_width() and 0 <= y0 < surface.get_height():
                surface.set_at((x0, y0), color)
        else:
            pygame.draw.circle(surface, color, (x0, y0), thickness // 2)

        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


# ══════════════════════════════════════════════════════════════
#  CG ALGORITHM 2 — MIDPOINT CIRCLE GENERATION
# ══════════════════════════════════════════════════════════════
def midpoint_circle(surface, cx, cy, r, color, fill=False):
    """
    Midpoint Circle Algorithm — uses the decision parameter
    p = 1 - r to determine which pixel is closer to the true circle.
    Exploits 8-fold symmetry for efficiency.
    """
    x, y = 0, r
    p = 1 - r
    points = []

    def plot_8(cx, cy, x, y):
        pts = [
            (cx+x, cy+y), (cx-x, cy+y),
            (cx+x, cy-y), (cx-x, cy-y),
            (cx+y, cy+x), (cx-y, cy+x),
            (cx+y, cy-x), (cx-y, cy-x),
        ]
        return pts

    while x <= y:
        pts = plot_8(cx, cy, x, y)
        if fill:
            points.extend(pts)
        else:
            for px, py in pts:
                if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                    surface.set_at((px, py), color)
        if p < 0:
            p += 2 * x + 3
        else:
            p += 2 * (x - y) + 5
            y -= 1
        x += 1

    if fill and points:
        # Fill by drawing horizontal spans between symmetric points
        for rad in range(r + 1):
            inner_x = int(math.sqrt(max(0, r*r - rad*rad)))
            for fx in range(cx - inner_x, cx + inner_x + 1):
                for fy in [cy + rad, cy - rad]:
                    if 0 <= fx < surface.get_width() and 0 <= fy < surface.get_height():
                        surface.set_at((fx, fy), color)


# ══════════════════════════════════════════════════════════════
#  CG ALGORITHM 3 — MIDPOINT ELLIPSE GENERATION
# ══════════════════════════════════════════════════════════════
def midpoint_ellipse(surface, cx, cy, rx, ry, color, fill=False):
    """
    Midpoint Ellipse Algorithm — two-region approach using the
    ellipse equation: (x/rx)^2 + (y/ry)^2 = 1
    Region 1: |slope| < 1   Region 2: |slope| > 1
    """
    x, y = 0, ry
    rx2, ry2 = rx * rx, ry * ry

    def plot_4(cx, cy, x, y):
        return [(cx+x, cy+y), (cx-x, cy+y), (cx+x, cy-y), (cx-x, cy-y)]

    def draw_pts(pts):
        for px, py in pts:
            if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                if fill:
                    # Draw horizontal line for fill
                    pass
                else:
                    surface.set_at((px, py), color)

    # Region 1
    p1 = ry2 - rx2 * ry + 0.25 * rx2
    while 2 * ry2 * x < 2 * rx2 * y:
        pts = plot_4(cx, cy, x, y)
        draw_pts(pts)
        if fill:
            for fx in range(cx - x, cx + x + 1):
                for fy in [cy + y, cy - y]:
                    if 0 <= fx < surface.get_width() and 0 <= fy < surface.get_height():
                        surface.set_at((fx, fy), color)
        if p1 < 0:
            x += 1
            p1 += 2 * ry2 * x + ry2
        else:
            x += 1
            y -= 1
            p1 += 2 * ry2 * x - 2 * rx2 * y + ry2

    # Region 2
    p2 = ry2 * (x + 0.5)**2 + rx2 * (y - 1)**2 - rx2 * ry2
    while y >= 0:
        pts = plot_4(cx, cy, x, y)
        draw_pts(pts)
        if fill:
            for fx in range(cx - x, cx + x + 1):
                for fy in [cy + y, cy - y]:
                    if 0 <= fx < surface.get_width() and 0 <= fy < surface.get_height():
                        surface.set_at((fx, fy), color)
        if p2 > 0:
            y -= 1
            p2 -= 2 * rx2 * y + rx2
        else:
            x += 1
            y -= 1
            p2 += 2 * ry2 * x - 2 * rx2 * y + rx2


# ══════════════════════════════════════════════════════════════
#  CG ALGORITHM 4 — SCAN-LINE POLYGON FILL
# ══════════════════════════════════════════════════════════════
def scanline_fill(surface, vertices, color):
    """
    Scan-Line Polygon Fill — finds intersections of horizontal
    scan lines with polygon edges, sorts them, fills spans.
    Used here to draw the pipe highlight stripe and ground.
    """
    if len(vertices) < 3:
        return
    min_y = max(0, int(min(v[1] for v in vertices)))
    max_y = min(surface.get_height() - 1, int(max(v[1] for v in vertices)))
    n = len(vertices)

    for y in range(min_y, max_y + 1):
        intersections = []
        for i in range(n):
            x0, y0 = vertices[i]
            x1, y1 = vertices[(i + 1) % n]
            if y0 == y1:
                continue
            if min(y0, y1) <= y < max(y0, y1):
                x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                intersections.append(int(x))
        intersections.sort()
        for k in range(0, len(intersections) - 1, 2):
            x_start = max(0, intersections[k])
            x_end   = min(surface.get_width() - 1, intersections[k + 1])
            if x_start <= x_end:
                pygame.draw.line(surface, color, (x_start, y), (x_end, y))


# ══════════════════════════════════════════════════════════════
#  CG ALGORITHM 5 — COHEN-SUTHERLAND LINE CLIPPING
# ══════════════════════════════════════════════════════════════
INSIDE = 0; LEFT = 1; RIGHT = 2; BOTTOM = 4; TOP = 8

def _compute_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= TOP
    elif y > ymax: code |= BOTTOM
    return code

def cohen_sutherland_clip(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    """
    Cohen-Sutherland Line Clipping — assigns region codes to endpoints
    and clips lines to a rectangular window using bitwise operations.
    Used to clip pipe decorations to pipe bounds.
    """
    c0 = _compute_code(x0, y0, xmin, ymin, xmax, ymax)
    c1 = _compute_code(x1, y1, xmin, ymin, xmax, ymax)
    while True:
        if not (c0 | c1):          # trivially inside
            return x0, y0, x1, y1
        if c0 & c1:                # trivially outside
            return None
        c_out = c0 if c0 else c1
        if c_out & BOTTOM:
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
            y = ymax
        elif c_out & TOP:
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
            y = ymin
        elif c_out & RIGHT:
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
            x = xmax
        else:
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
            x = xmin
        if c_out == c0:
            x0, y0 = x, y
            c0 = _compute_code(x0, y0, xmin, ymin, xmax, ymax)
        else:
            x1, y1 = x, y
            c1 = _compute_code(x1, y1, xmin, ymin, xmax, ymax)


# ══════════════════════════════════════════════════════════════
#  CG ALGORITHM 6 — 2D TRANSFORMATIONS
# ══════════════════════════════════════════════════════════════
def rotate_point(x, y, cx, cy, angle_deg):
    """
    2D Rotation Transform:
    x' = cos(θ)(x-cx) - sin(θ)(y-cy) + cx
    y' = sin(θ)(x-cx) + cos(θ)(y-cy) + cy
    """
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    nx = cos_a * (x - cx) - sin_a * (y - cy) + cx
    ny = sin_a * (x - cx) + cos_a * (y - cy) + cy
    return nx, ny

def scale_point(x, y, cx, cy, sx, sy):
    """2D Scaling Transform about a center point."""
    return cx + sx * (x - cx), cy + sy * (y - cy)

def translate_polygon(vertices, tx, ty):
    """2D Translation Transform."""
    return [(x + tx, y + ty) for x, y in vertices]


# ══════════════════════════════════════════════════════════════
#  DRAWING HELPERS USING CG ALGORITHMS
# ══════════════════════════════════════════════════════════════
def draw_gradient_bg(surface):
    """Draw sky gradient using horizontal scan lines."""
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(SKY_TOP[0] * (1-t) + SKY_BOT[0] * t)
        g = int(SKY_TOP[1] * (1-t) + SKY_BOT[1] * t)
        b = int(SKY_TOP[2] * (1-t) + SKY_BOT[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_cloud(surface, cx, cy, scale=1.0):
    """Draw a cloud using Midpoint Ellipse Algorithm (CG Algo 3)."""
    rx, ry = int(30 * scale), int(18 * scale)
    midpoint_ellipse(surface, cx, cy, rx, ry, CLOUD_COL, fill=True)
    midpoint_ellipse(surface, cx - int(22*scale), cy + int(5*scale),
                     int(22*scale), int(14*scale), CLOUD_COL, fill=True)
    midpoint_ellipse(surface, cx + int(22*scale), cy + int(5*scale),
                     int(22*scale), int(14*scale), CLOUD_COL, fill=True)


def draw_pipe(surface, x, top_height, bot_y, pipe_w=60):
    """
    Draw a pipe using:
    - Scan-Line Fill (CG Algo 4) for body
    - Bresenham Lines (CG Algo 1) for edges
    - Cohen-Sutherland (CG Algo 5) for clipped highlights
    """
    cap_h = 20
    cap_ext = 6

    # Top pipe body
    body = [(x, 0), (x+pipe_w, 0), (x+pipe_w, top_height), (x, top_height)]
    scanline_fill(surface, body, PIPE_COL)

    # Top pipe cap
    cap = [(x-cap_ext, top_height-cap_h),
           (x+pipe_w+cap_ext, top_height-cap_h),
           (x+pipe_w+cap_ext, top_height),
           (x-cap_ext, top_height)]
    scanline_fill(surface, cap, PIPE_COL)

    # Bottom pipe body
    bbody = [(x, bot_y), (x+pipe_w, bot_y), (x+pipe_w, HEIGHT), (x, HEIGHT)]
    scanline_fill(surface, bbody, PIPE_COL)

    # Bottom pipe cap
    bcap = [(x-cap_ext, bot_y), (x+pipe_w+cap_ext, bot_y),
            (x+pipe_w+cap_ext, bot_y+cap_h), (x-cap_ext, bot_y+cap_h)]
    scanline_fill(surface, bcap, PIPE_COL)

    # Dark right edge — Bresenham Line (CG Algo 1)
    bresenham_line(surface, x+pipe_w, 0, x+pipe_w, top_height, PIPE_DARK, 3)
    bresenham_line(surface, x+pipe_w+cap_ext, top_height-cap_h,
                   x+pipe_w+cap_ext, top_height, PIPE_DARK, 3)
    bresenham_line(surface, x+pipe_w, bot_y, x+pipe_w, HEIGHT, PIPE_DARK, 3)
    bresenham_line(surface, x+pipe_w+cap_ext, bot_y,
                   x+pipe_w+cap_ext, bot_y+cap_h, PIPE_DARK, 3)

    # Highlight stripe — Cohen-Sutherland Clipping (CG Algo 5)
    hl_x = x + 8
    clipped = cohen_sutherland_clip(hl_x, 0, hl_x, top_height,
                                     x, 0, x+pipe_w, top_height)
    if clipped:
        bresenham_line(surface, int(clipped[0]), int(clipped[1]),
                       int(clipped[2]), int(clipped[3]), PIPE_LIGHT, 4)
    clipped2 = cohen_sutherland_clip(hl_x, bot_y, hl_x, HEIGHT,
                                      x, bot_y, x+pipe_w, HEIGHT)
    if clipped2:
        bresenham_line(surface, int(clipped2[0]), int(clipped2[1]),
                       int(clipped2[2]), int(clipped2[3]), PIPE_LIGHT, 4)


def draw_bird(surface, bx, by, angle):
    """
    Draw the bird using:
    - Midpoint Circle Algorithm (CG Algo 2) for body
    - 2D Rotation Transform (CG Algo 6) for tilt
    - Bresenham Lines (CG Algo 1) for beak
    - Midpoint Ellipse (CG Algo 3) for wing
    """
    # Body (circle)
    midpoint_circle(surface, int(bx), int(by), 18, BIRD_BODY, fill=True)
    midpoint_circle(surface, int(bx), int(by), 18, (220, 170, 40))

    # Wing — rotated ellipse using 2D transform points
    wing_pts_base = [(-4, 6), (14, 2), (16, 12), (-4, 16)]
    rotated_wing  = [rotate_point(bx + px, by + py, bx, by, angle)
                     for px, py in wing_pts_base]
    scanline_fill(surface, [(int(p[0]), int(p[1])) for p in rotated_wing], BIRD_WING)

    # Eye white
    ex, ey = rotate_point(bx + 9, by - 5, bx, by, angle)
    midpoint_circle(surface, int(ex), int(ey), 5, BIRD_EYE, fill=True)
    # Pupil
    px2, py2 = rotate_point(bx + 11, by - 5, bx, by, angle)
    midpoint_circle(surface, int(px2), int(py2), 2, BIRD_PUPIL, fill=True)

    # Beak — Bresenham line
    bk1x, bk1y = rotate_point(bx + 17, by - 2, bx, by, angle)
    bk2x, bk2y = rotate_point(bx + 24, by + 1, bx, by, angle)
    bk3x, bk3y = rotate_point(bx + 17, by + 4, bx, by, angle)
    scanline_fill(surface, [(int(bk1x), int(bk1y)), (int(bk2x), int(bk2y)),
                             (int(bk3x), int(bk3y))], BIRD_BEAK)
    bresenham_line(surface, int(bk1x), int(bk1y), int(bk2x), int(bk2y), (200, 80, 0), 2)
    bresenham_line(surface, int(bk2x), int(bk2y), int(bk3x), int(bk3y), (200, 80, 0), 2)


def draw_ground(surface, offset):
    """Draw scrolling ground using scan-line fill and Bresenham lines."""
    ground_y = HEIGHT - 80
    # Ground base
    ground_verts = [(0, ground_y), (WIDTH, ground_y), (WIDTH, HEIGHT), (0, HEIGHT)]
    scanline_fill(surface, ground_verts, GROUND_COL)
    # Grass strip
    grass_verts = [(0, ground_y), (WIDTH, ground_y),
                   (WIDTH, ground_y + 14), (0, ground_y + 14)]
    scanline_fill(surface, grass_verts, GRASS_COL)

    # Texture lines using Bresenham
    stripe_spacing = 40
    for i in range(-stripe_spacing, WIDTH + stripe_spacing, stripe_spacing):
        sx = (i + offset) % (WIDTH + stripe_spacing) - stripe_spacing
        bresenham_line(surface, sx, ground_y + 2, sx + 20, ground_y + 12,
                       (80, 170, 50), 2)

    # Ground shadow line
    bresenham_line(surface, 0, ground_y, WIDTH, ground_y, GROUND_DARK, 3)


def draw_score(surface, score, font_big, font_small, game_over=False,
               started=False, best=0):
    """Render score with clean styling."""
    if not started:
        # Title screen
        title_surf = font_big.render("FLAPPY BIRD", True, WHITE)
        sub_surf   = font_small.render("Press SPACE or TAP to flap!", True, WHITE)
        cg_surf    = font_small.render("[ CG Practical Project ]", True, (255, 230, 100))
        surface.blit(title_surf,
                     (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 100))
        surface.blit(sub_surf,
                     (WIDTH//2 - sub_surf.get_width()//2, HEIGHT//2 - 40))
        surface.blit(cg_surf,
                     (WIDTH//2 - cg_surf.get_width()//2, HEIGHT//2 + 0))
        return

    if game_over:
        go_surf   = font_big.render("GAME OVER", True, RED)
        sc_surf   = font_small.render(f"Score: {score}", True, WHITE)
        bs_surf   = font_small.render(f"Best:  {best}", True, (255, 230, 100))
        re_surf   = font_small.render("SPACE to Restart", True, WHITE)
        surface.blit(go_surf,
                     (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 100))
        surface.blit(sc_surf,
                     (WIDTH//2 - sc_surf.get_width()//2, HEIGHT//2 - 30))
        surface.blit(bs_surf,
                     (WIDTH//2 - bs_surf.get_width()//2, HEIGHT//2 + 10))
        surface.blit(re_surf,
                     (WIDTH//2 - re_surf.get_width()//2, HEIGHT//2 + 60))
    else:
        sc_surf = font_big.render(str(score), True, WHITE)
        # Drop shadow
        sh_surf = font_big.render(str(score), True, (0, 0, 0))
        surface.blit(sh_surf, (WIDTH//2 - sc_surf.get_width()//2 + 2,
                                 HEIGHT//10 + 2))
        surface.blit(sc_surf, (WIDTH//2 - sc_surf.get_width()//2,
                                 HEIGHT//10))


# ══════════════════════════════════════════════════════════════
#  AABB COLLISION DETECTION (CG Concept)
# ══════════════════════════════════════════════════════════════
def check_collision(bx, by, bird_r, pipe_x, top_h, bot_y, pipe_w=60, cap_ext=6):
    """
    Axis-Aligned Bounding Box (AABB) collision detection.
    Checks bird circle against pipe rectangles.
    """
    # Bird bounding box (tight)
    bl = bx - bird_r + 4
    br = bx + bird_r - 4
    bt = by - bird_r + 4
    bb = by + bird_r - 4

    # Top pipe rect (including cap)
    tp_left  = pipe_x - cap_ext
    tp_right = pipe_x + pipe_w + cap_ext
    tp_bot   = top_h

    # Bottom pipe rect
    bp_left  = pipe_x - cap_ext
    bp_right = pipe_x + pipe_w + cap_ext
    bp_top   = bot_y

    top_hit = (br > tp_left and bl < tp_right and bt < tp_bot)
    bot_hit = (br > bp_left and bl < bp_right and bb > bp_top)
    return top_hit or bot_hit


# ══════════════════════════════════════════════════════════════
#  STAR FIELD (background decoration)
# ══════════════════════════════════════════════════════════════
def generate_stars(n=30):
    return [(random.randint(0, WIDTH), random.randint(0, HEIGHT - 120),
             random.randint(1, 2)) for _ in range(n)]

def draw_stars(surface, stars):
    for sx, sy, sr in stars:
        midpoint_circle(surface, sx, sy, sr, STAR_COL, fill=True)


# ══════════════════════════════════════════════════════════════
#  MAIN GAME
# ══════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird — CG Practical Project")
    clock  = pygame.time.Clock()

    try:
        font_big   = pygame.font.SysFont("comicsansms", 48, bold=True)
        font_small = pygame.font.SysFont("comicsansms", 24)
    except Exception:
        font_big   = pygame.font.Font(None, 56)
        font_small = pygame.font.Font(None, 30)

    # Pre-render static background (gradient + stars) — Double Buffering demo
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    draw_gradient_bg(bg_surface)
    stars = generate_stars(25)
    draw_stars(bg_surface, stars)
    # Static clouds (parallax layer 1 — slow)
    cloud_positions = [(80, 80, 1.0), (230, 60, 0.8), (380, 100, 1.2),
                       (50, 160, 0.6), (300, 150, 0.9)]
    for (ccx, ccy, ccs) in cloud_positions:
        draw_cloud(bg_surface, ccx, ccy, ccs)

    # Game state
    def reset():
        return {
            "bird_y":    HEIGHT // 2,
            "bird_vy":   0,
            "bird_angle": 0,
            "pipes":     [],          # list of (x, top_h, bot_y, scored)
            "ground_off": 0,
            "score":     0,
            "game_over": False,
            "started":   False,
            "spawn_timer": pygame.time.get_ticks(),
            "cloud_off": 0,
        }

    state = reset()
    best  = 0
    BIRD_X = WIDTH // 4

    # ── GAME LOOP ──────────────────────────────────────────────
    while True:
        dt = clock.tick(FPS)

        # ── EVENTS ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                key_ok = (event.type == pygame.KEYDOWN and
                          event.key in (pygame.K_SPACE, pygame.K_UP,
                                        pygame.K_w))
                mouse_ok = event.type == pygame.MOUSEBUTTONDOWN
                if key_ok or mouse_ok:
                    if state["game_over"]:
                        if state["score"] > best:
                            best = state["score"]
                        state = reset()
                    elif not state["started"]:
                        state["started"] = True
                        state["bird_vy"] = FLAP_STRENGTH
                    else:
                        state["bird_vy"] = FLAP_STRENGTH

        # ── UPDATE ──
        if state["started"] and not state["game_over"]:
            # Physics
            state["bird_vy"] += GRAVITY
            state["bird_y"]  += state["bird_vy"]

            # Bird angle (2D rotation concept) — tilt based on velocity
            state["bird_angle"] = max(-30, min(90,
                                    state["bird_vy"] * 4.5))

            # Ground scroll (parallax)
            state["ground_off"] = (state["ground_off"] + PIPE_SPEED) % 40
            state["cloud_off"]  = (state["cloud_off"] + 0.4)

            # Spawn pipes
            now = pygame.time.get_ticks()
            if now - state["spawn_timer"] > PIPE_INTERVAL:
                top_h = random.randint(80, HEIGHT - 80 - PIPE_GAP - 80)
                bot_y = top_h + PIPE_GAP
                state["pipes"].append([WIDTH + 10, top_h, bot_y, False])
                state["spawn_timer"] = now

            # Move pipes
            for p in state["pipes"]:
                p[0] -= PIPE_SPEED

            # Remove off-screen pipes
            state["pipes"] = [p for p in state["pipes"] if p[0] > -80]

            # Score + collision
            for p in state["pipes"]:
                if not p[3] and p[0] + 60 < BIRD_X:
                    p[3] = True
                    state["score"] += 1
                if check_collision(BIRD_X, state["bird_y"], 17,
                                   p[0], p[1], p[2]):
                    state["game_over"] = True

            # Ground / ceiling
            if state["bird_y"] > HEIGHT - 80 - 15:
                state["bird_y"] = HEIGHT - 80 - 15
                state["game_over"] = True
            if state["bird_y"] < 10:
                state["bird_y"] = 10
                state["bird_vy"] = 0

        # ── RENDER (Double Buffering — drawn to off-screen, then flipped) ──
        # Layer 0: Background (pre-rendered surface)
        screen.blit(bg_surface, (0, 0))

        # Layer 1: Parallax clouds (move slower than pipes — parallax scrolling)
        cloud_off_x = int(state["cloud_off"]) % (WIDTH + 120)
        for i, (ccx, ccy, ccs) in enumerate(cloud_positions):
            cx = (ccx - cloud_off_x * 0.3 * (0.5 + i*0.1)) % (WIDTH + 120) - 60
            draw_cloud(screen, int(cx), ccy, ccs)

        # Layer 2: Pipes (using CG algorithms)
        for p in state["pipes"]:
            draw_pipe(screen, int(p[0]), p[1], p[2])

        # Layer 3: Ground (scan-line fill + scrolling)
        draw_ground(screen, state["ground_off"])

        # Layer 4: Bird (circle + ellipse + line + rotation)
        draw_bird(screen, BIRD_X, state["bird_y"], state["bird_angle"])

        # Layer 5: HUD / Score
        draw_score(screen, state["score"], font_big, font_small,
                   game_over=state["game_over"],
                   started=state["started"],
                   best=best)

        # Flip to screen (Double Buffering finalisation)
        pygame.display.flip()


if __name__ == "__main__":
    main()
