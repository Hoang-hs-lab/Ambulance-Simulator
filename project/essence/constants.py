import pygame

pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

WHITE = (255, 255, 255)
GREEN = (34, 139, 34) 
DARK_GREEN = (20, 90, 20)
YELLOW = (255, 215, 0)
RED = (210, 50, 50)
GRAY = (80, 80, 80)
LIGHT_GRAY = (180, 180, 180)
BROWN = (245, 210, 138)
ORANGE = (255, 140, 0)
ROAD_COLOR = (55, 55, 55)
UI_BACKGROUND = (18, 18, 38)
UI_PANEL = (38, 38, 65)
COIN_COLOR = (255, 215, 0)
BUTTON_COLOR = (55, 115, 195)
BUTTON_HOVER = (75, 145, 225)
INPUT_BACKGROUND = (28, 28, 48)
INPUT_ACTIVE = (48, 48, 78)
ENEMY_COLORS = ["blue", "red", "green"]
HOUSE_BODY_COLORS = [(240, 220, 180), (200, 180, 160), (215, 195, 165)]
HOUSE_ROOF_COLORS = [RED, (148, 78, 50), (175, 98, 58)]

TOPBAR_HEIGHT = 185
ROAD_TOP = TOPBAR_HEIGHT
ROAD_BOTTOM = 730
ROAD_HEIGHT = ROAD_BOTTOM - ROAD_TOP
DIVIDER_Y = ROAD_TOP + ROAD_HEIGHT // 2
UPPER_LANE_Y = ROAD_TOP + ROAD_HEIGHT // 4
LOWER_LANE_Y = ROAD_TOP + ROAD_HEIGHT * 3 // 4
CENTER_X = SCREEN_WIDTH // 2

RECT_PAUSE = pygame.Rect(1785, 14, 118, 50)
RECT_COIN = pygame.Rect(200, 18, 225, 62)
RECT_PROGRESS = pygame.Rect(700, 22, 500, 24)  # progress
RECT_LOGIN = pygame.Rect(795, 650, 330, 55)
RECT_CREATE = pygame.Rect(795, 720, 330, 55)
RECT_FORGOT = pygame.Rect(795, 790, 330, 55)
RECT_CREATE_ACCOUNT_OK = pygame.Rect(795, 695, 330, 55)
RECT_CREATE_ACCOUNT_BACK = pygame.Rect(795, 768, 330, 55)
RECT_FORGOT_PASSWORD_OK = pygame.Rect(795, 695, 330, 55)
RECT_FORGOT_PASSWORD_BACK = pygame.Rect(795, 768, 330, 55)
RECT_RETRY = pygame.Rect(820, 595, 280, 60)
RECT_GAME_MENU = pygame.Rect(820, 670, 280, 60)
RECT_RESUME = pygame.Rect(820, 445, 280, 60)
RECT_PAUSE_SAVE = pygame.Rect(820, 525, 280, 60)
RECT_PAUSE_QUIT = pygame.Rect(820, 605, 280, 60)
RECT_START = pygame.Rect(700, 550, 240, 65)
RECT_LOGOUT = pygame.Rect(1772, 16, 128, 46)

# SHOP
RECT_SHOP = pygame.Rect(980, 550, 240, 65)
RECT_SHOP_BACK = pygame.Rect(820, 780, 280, 60)
RECT_TAB_FUEL = pygame.Rect(690, 240, 250, 50)

# LEADERBOARD
RECT_LEADER = pygame.Rect(700, 630, 240, 55)
RECT_FRIENDS_BUTTON = pygame.Rect(980, 630, 240, 55)
RECT_LEADERBOARD_BACK = pygame.Rect(200, 870, 280, 55)

# FRIENDS
RECT_FRIENDS_BACK = pygame.Rect(820, 870, 280, 55)
RECT_FRIENDS_FIND = pygame.Rect(1125, 373, 165, 46)
RECT_FRIENDS_ADD = pygame.Rect(760, 445, 160, 46)
RECT_FRIENDS_REMOVE = pygame.Rect(940, 445, 160, 46)

# 0 is UI, 1 and 5: increment in size
FONT_TITLE = pygame.font.SysFont("Arial", 72, bold=True)
FONT_LARGE = pygame.font.SysFont("Arial", 52, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Arial", 34)
FONT_SMALL = pygame.font.SysFont("Arial", 24)
FONT_TINY = pygame.font.SysFont("Arial", 17)
FONT_UI = pygame.font.SysFont("Arial", 26, bold=True)

PLAYER_SPEED = 360
TIMER_SECONDS = 65
WIN_DISTANCE = 60000
SCROLL_BASE = 8
BOOST_DURATION = 10
ACCOUNT_FILE = "data.json"


FUEL_PACKS = [
    {"label": "Fuel x3", "amount": 3, "cost": 50},
    {"label": "Fuel x10", "amount": 10, "cost": 150},
    {"label": "Fuel x25", "amount": 25, "cost": 350},
]

# Each entry has an id, display name, description, and a check(player_data)->bool
ACHIEVEMENTS = [
    {
        "id": "first_win",
        "name": "First Responder",
        "desc": "Win your first run",
        "check": lambda d: d.get("wins", 0) >= 1,
    },
    {
        "id": "win_5",
        "name": "Veteran Driver",
        "desc": "Win 5 runs",
        "check": lambda d: d.get("wins", 0) >= 5,
    },
    {
        "id": "win_10",
        "name": "Road Legend",
        "desc": "Win 10 runs",
        "check": lambda d: d.get("wins", 0) >= 10,
    },
    {
        "id": "coin_100",
        "name": "Pocket Change",
        "desc": "Earn 100 total coins lifetime",
        "check": lambda d: d.get("total_coin", 0) >= 100,
    },
    {
        "id": "coin_500",
        "name": "Coin Hoarder",
        "desc": "Earn 500 total coins lifetime",
        "check": lambda d: d.get("total_coin", 0) >= 500,
    },
    {
        "id": "coin_1000",
        "name": "Millionaire",
        "desc": "Earn 1 000 total coins",
        "check": lambda d: d.get("total_coin", 0) >= 1000,
    },
    {
        "id": "friend_1",
        "name": "Not Alone",
        "desc": "Add your first friend",
        "check": lambda d: len(d.get("friends", [])) >= 1,
    },
    {
        "id": "friend_5",
        "name": "Social Butterfly",
        "desc": "Have 5 friends",
        "check": lambda d: len(d.get("friends", [])) >= 5,
    },
]

STATE_LOGIN = "login"
STATE_CREATE = "create"
STATE_FORGOT = "forgot"
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_PAUSE = "pause"
STATE_DEAD_TIME = "d_time"
STATE_DEAD_CRASH = "d_crash"
STATE_WIN = "win"
STATE_SHOP = "shop"
STATE_LEADERBOARD = "leaderboard"
STATE_FRIENDS = "friends"
