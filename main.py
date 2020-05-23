import pygame
import pygame.gfxdraw
import random

pygame.init()
size = [1024, 960]
screen = pygame.display.set_mode(size)

STAR_COLORS = [pygame.Color("#FFFFFF"), pygame.Color("#D9FFFF"), pygame.Color("#A3FFFF"),
               pygame.Color("#FFC8C8"), pygame.Color("#FFCB9D"), pygame.Color("#9F9FFF"),
               pygame.Color("#415EFF"), pygame.Color("#28199D")]

pygame.display.set_caption("Procedural Generation")


class StarSystem:
    def __init__(self, x, y, generatePlanets=False):
        self.nLehmer = (x & 0xFFFF) << 16 | (y & 0xFFFF)
        self.starExists = self.randInt(0, 20) == 1
        if not self.starExists:
            return

        self.starDiameter = self.randInt(10, 40)
        self.starColor = STAR_COLORS[self.randInt(0, 7)]

        if not generatePlanets:
            return
        self.distanceFromStar = self.randInt(60, 200)
        self.numberOfPlanets = self.randInt(0, 11)
        self.Planets = []
        random.seed(self.nLehmer)
        for num in range(self.numberOfPlanets):
            planet = Planet()
            planet.distance = self.distanceFromStar
            self.distanceFromStar += self.randInt(20, 200)
            planet.diameter = random.uniform(4.0, 20.5)
            planet.temperature = self.randInt(-250, 1500)
            planet.population = max([self.randInt(-5000000, 20000000), 0])
            planet.ring = self.randInt(0, 10) == 1
            planet.number_of_moons = self.randInt(0, 6)
            for num2 in range(planet.number_of_moons):
                planet.Moons.append(self.randInt(1, 10))
            self.Planets.append(planet)

    def LehmerNumberGen(self, stateNumber):
        stateNumber += 0xe120fc15
        tmp = stateNumber * 0x4a39b70d
        m1 = (tmp >> 32) ^ tmp
        tmp = m1 * 0x12fad5c9
        m2 = (tmp >> 32) ^ tmp
        self.nLehmer = stateNumber
        return m2

    def randInt(self, minimum, maximum):
        return (self.LehmerNumberGen(self.nLehmer) % (maximum - minimum)) + minimum

class Planet:
    def __init__(self):
        self.distance = 0
        self.diameter = 0
        self.temperature = 0
        self.population = 0
        self.hasRing = False
        self.number_of_moons = 0
        self.Moons = []

done = False
clock = pygame.time.Clock()
viewportOffset = [0, 0]
mouse_position = (0, 0)
mouse_sector_position = [0, 0]
world_mouse_position = [mouse_position[0] + viewportOffset[0], mouse_position[1] + viewportOffset[1]]
mouse_state = None
star_selected = False
star_system_window = pygame.Rect(8, 650, 992, 300)
while not done:
    clock.tick(30)
    # Track Mouse Position
    mouse_position = pygame.mouse.get_pos()
    mouse_sector_position = [mouse_position[0] / 32, mouse_position[1] / 32]
    world_mouse_position = [int(mouse_sector_position[0]) + viewportOffset[0],
                            int(mouse_sector_position[1]) + viewportOffset[1]]

    screen.fill(pygame.Color("#000000"))
    # Divide Screen Into Grid
    sectorX = size[0] / 32
    sectorY = size[1] / 32
    screen_sector = [0, 0]
    for i in range(int(sectorX)):
        screen_sector[0] = i
        for j in range(int(sectorY)):
            screen_sector[1] = j
            # Generate Star in each sector
            star = StarSystem(screen_sector[0] + viewportOffset[0], screen_sector[1] + viewportOffset[1])
            if star.starExists:
                # Draw Star
                pygame.gfxdraw.filled_circle(screen,
                                             screen_sector[0] * 32 + 16,
                                             screen_sector[1] * 32 + 16,
                                             int(star.starDiameter / 3),
                                             star.starColor)
                # Highlight star if mouse is hovered over star
                if int(mouse_sector_position[0]) == screen_sector[0] and int(mouse_sector_position[1]) == screen_sector[1]:
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (screen_sector[0] * 32 + 16, screen_sector[1] * 32 + 16), 16, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_state = pygame.mouse.get_pressed()
            # Check if mouse was left clicked
            if mouse_state == (1, 0, 0):
                star = StarSystem(world_mouse_position[0], world_mouse_position[1])
                if star.starExists:
                    star_selected = True
                    selected_star = world_mouse_position
                else:
                    star_selected = False

    if star_selected:
        # Draw Star System UI
        star = StarSystem(selected_star[0], selected_star[1], True)
        pygame.draw.rect(screen, pygame.Color("#808080"), star_system_window)
        star_position = [14, 766]
        star_position[0] += star.starDiameter * 1.375 * 2
        pygame.gfxdraw.filled_circle(screen, int(star_position[0]), int(star_position[1]),
                                     int(star.starDiameter * 1.375 * 2), star.starColor)
        star_position[0] += star.starDiameter * 1.375 * 2 + 16
        for planet in star.Planets:
            star_position[0] += planet.diameter * 2
            pygame.gfxdraw.filled_circle(screen, int(star_position[0]), int(star_position[1]),
                                         int(planet.diameter * 2), (255, 0, 0))
            moon_position = [0, 0]
            moon_position[0] = star_position[0]
            moon_position[1] = star_position[1]
            moon_position[1] += planet.diameter * 2 + 20
            for moon in planet.Moons:
                moon_position[1] += moon
                pygame.gfxdraw.filled_circle(screen, int(moon_position[0]), int(moon_position[1]),
                                             moon, (255, 255, 255))
                moon_position[1] += moon + 10

            star_position[0] += planet.diameter * 2 + 16
    pygame.display.update()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        viewportOffset[1] -= 1
    if keys[pygame.K_s]:
        viewportOffset[1] += 1
    if keys[pygame.K_d]:
        viewportOffset[0] += 1
    if keys[pygame.K_a]:
        viewportOffset[0] -= 1