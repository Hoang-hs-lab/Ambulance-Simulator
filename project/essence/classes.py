import pygame
import random
from essence.constants import *


class Input_box:
    def __init__(self, x, y, w, h, label, is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = ""
        self.active = False
        self.is_password = is_password


class Enemy:
    def __init__(self, lane, vehicle_sizes):
        self.lane = lane
        self.vehicle_type = random.choice(["car", "bus"])
        self.color = random.choice(ENEMY_COLORS)
        self.width, self.height = vehicle_sizes[self.vehicle_type]
        self.face_left = lane == "upper"
        self.speed = (
            random.uniform(6, 11) if lane == "upper" else random.uniform(1.5, 4.5)
        )
        self.x = float(SCREEN_WIDTH + 60)
        self.y = float(
            random.randint(ROAD_TOP + 10, DIVIDER_Y - self.height - 10)
            if lane == "upper"
            else random.randint(DIVIDER_Y + 10, ROAD_BOTTOM - self.height - 10)
        )


class Coin:
    def __init__(self):
        self.x = float(SCREEN_WIDTH + 30)
        self.collected = False
        self.y = float(random.randint(ROAD_TOP + 35, ROAD_BOTTOM - 35))


class Shield_on_road:
    def __init__(self):
        self.radius = 20
        self.collected = False
        self.x = float(SCREEN_WIDTH + 40)
        self.y = float(random.randint(ROAD_TOP + 45, ROAD_BOTTOM - 45))


class House:
    def __init__(self):
        self.x = float(SCREEN_WIDTH + 20)
        self.row = random.randint(0, 1)
        self.style = random.randint(0, 2)


class Hospital:
    def __init__(self):
        self.x = float(SCREEN_WIDTH + 100)


class Player:
    def __init__(self, frames):
        self.x = 120
        self.y = float(LOWER_LANE_Y - 65)
        self.width = 200
        self.height = 130
        self.frame = 0
        self.frame_timer = 0
        self.shield_on = False
        self.shield_timer = 0
        self.invincibility_timer = 0
        self.lives = 2
        self.boost = 1
        self.boost_timer = 0
        self.frames = frames
        self.image = self.frames[0]


class Game_state:
    def __init__(self, fuel, frames):
        self.player = Player(frames)
        self.enemies = []
        self.coins = []
        self.shields = []
        self.houses = []
        self.hospital = None
        self.scroll = SCROLL_BASE
        self.line_offset = 0
        self.time_left = float(TIMER_SECONDS)
        self.run_coin = 0
        self.distance = 0
        self.fuel = fuel
        # control spawn frequency
        self.enemy_spawn_timer = random.uniform(0.5, 3)
        self.coin_spawn_timer = random.uniform(0.5, 0.7)
        self.shield_spawn_timer = random.uniform(9, 16)
        self.house_spawn_timer = random.uniform(1.2, 3.5)
