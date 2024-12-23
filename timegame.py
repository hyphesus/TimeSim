import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity and Orbit Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)

# Clock
clock = pygame.time.Clock()

# Static masses (e.g., planets or stars)
static_masses = [
    {"pos": [400, 300], "mass": 50},
]

# Dynamic masses (e.g., moving objects affected by gravity)
dynamic_masses = []

# Gravity constant
GRAVITY = 0.1
MIN_SIZE = 2  # Minimum size before disappearing
ORBIT_RADIUS = 150  # Threshold to transition into orbit
selected_static_mass = None  # For dragging red dots

def calculate_gravitational_force(m1, m2, dist):
    """Calculate gravitational force between two masses."""
    if dist > 0:
        return GRAVITY * m1["mass"] * m2["mass"] / dist**2
    return 0

def spawn_random_mass():
    """Spawn a random mass at the edges of the screen."""
    edge = random.choice(["top", "bottom", "left", "right"])
    if edge == "top":
        pos = [random.randint(0, WIDTH), 0]
    elif edge == "bottom":
        pos = [random.randint(0, WIDTH), HEIGHT]
    elif edge == "left":
        pos = [0, random.randint(0, HEIGHT)]
    else:  # right
        pos = [WIDTH, random.randint(0, HEIGHT)]
    
    mass = {
        "pos": pos,
        "mass": random.randint(5, 20),
        "speed": [random.uniform(-1, 1), random.uniform(-1, 1)],
        "size": random.randint(5, 20),
        "orbiting": False,
        "orbit_center": None
    }
    dynamic_masses.append(mass)

def draw_grid():
    """Draw the grid visualizing spacetime bending."""
    for x in range(0, WIDTH, 20):
        for y in range(0, HEIGHT, 20):
            distortion = sum(static_mass["mass"] / max(1, math.sqrt((x - static_mass["pos"][0])**2 + (y - static_mass["pos"][1])**2)) for static_mass in static_masses)
            color_intensity = min(255, int(distortion * 50))
            color = (color_intensity, 0, 255 - color_intensity)  # Red to Blue gradient
            pygame.draw.circle(screen, color, (x, y), 2)

def draw_masses():
    """Draw all masses (static and dynamic)."""
    for static_mass in static_masses:
        pygame.draw.circle(screen, RED, (int(static_mass["pos"][0]), int(static_mass["pos"][1])), static_mass["mass"])
    for dynamic_mass in dynamic_masses:
        pygame.draw.circle(screen, GREEN, (int(dynamic_mass["pos"][0]), int(dynamic_mass["pos"][1])), dynamic_mass["size"])

def update_dynamic_masses():
    """Update positions and states of dynamic masses."""
    for mass in dynamic_masses[:]:
        if mass["orbiting"]:
            # Calculate orbit position
            orbit_center = mass["orbit_center"]
            dx = mass["pos"][0] - orbit_center["pos"][0]
            dy = mass["pos"][1] - orbit_center["pos"][1]
            distance = math.sqrt(dx**2 + dy**2)

            # Calculate tangential velocity for orbit
            tangent_vx = -dy / distance
            tangent_vy = dx / distance
            mass["speed"] = [tangent_vx, tangent_vy]
            mass["pos"][0] += mass["speed"][0]
            mass["pos"][1] += mass["speed"][1]
        else:
            # Apply gravity from all static masses
            for static_mass in static_masses:
                dx = static_mass["pos"][0] - mass["pos"][0]
                dy = static_mass["pos"][1] - mass["pos"][1]
                dist = math.sqrt(dx**2 + dy**2)
                force = calculate_gravitational_force(mass, static_mass, dist)
                # Adjust velocity based on gravity
                if dist > 0:
                    mass["speed"][0] += force * dx / dist
                    mass["speed"][1] += force * dy / dist

                # Check if the mass should transition into orbit
                if dist < ORBIT_RADIUS:
                    mass["orbiting"] = True
                    mass["orbit_center"] = static_mass

            # Move the mass
            mass["pos"][0] += mass["speed"][0]
            mass["pos"][1] += mass["speed"][1]

        # Shrink mass size based on proximity to static masses
        for static_mass in static_masses:
            dx = static_mass["pos"][0] - mass["pos"][0]
            dy = static_mass["pos"][1] - mass["pos"][1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 200:  # Within gravitational zone
                mass["size"] -= 0.05  # Shrink over time

        # Remove mass if it shrinks too small
        if mass["size"] < MIN_SIZE:
            dynamic_masses.remove(mass)

# Game loop
running = True
spawn_timer = 0  # Timer to spawn new masses
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for static_mass in static_masses:
                dx = event.pos[0] - static_mass["pos"][0]
                dy = event.pos[1] - static_mass["pos"][1]
                if math.sqrt(dx**2 + dy**2) < static_mass["mass"]:
                    selected_static_mass = static_mass
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_static_mass = None
        elif event.type == pygame.MOUSEMOTION and selected_static_mass:
            selected_static_mass["pos"] = list(event.pos)

    # Spawn new masses periodically
    spawn_timer += 1
    if spawn_timer > 50:  # Spawn every 50 frames
        spawn_random_mass()
        spawn_timer = 0

    # Update and draw the simulation
    draw_grid()
    draw_masses()
    update_dynamic_masses()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
