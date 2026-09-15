import pygame
import random
from essence.constants import *
from essence.classes import *
from essence.acc_handle import *


# Text render cache
TEXT_CACHE = {}


# TEXT RENDER
def render_text(font, text, color):
    key = (id(font), text, color)
    if key not in TEXT_CACHE:
        TEXT_CACHE[key] = font.render(text, True, color)
    return TEXT_CACHE[key]


# IMAGES
def image_ratio(path, width):
    raw = pygame.image.load(path).convert_alpha()
    raw_width, raw_height = raw.get_size()
    return pygame.transform.scale(raw, (width, int(raw_height * width / raw_width)))


def image_fixed(path, width, height):
    return pygame.transform.scale(
        pygame.image.load(path).convert_alpha(), (width, height)
    )


# PLAYER FRAMES
PLAYER_FRAMES = [
    image_fixed(f"assets/Ambulance/{i}.png", 200, 130) for i in range(1, 122)
]


# ENEMY VEHICLES
VEHICLE_IMAGES = {}
VEHICLE_SIZES = {}
for color in ENEMY_COLORS:
    car = image_ratio(f"assets/car/{color}_car.png", 120)
    bus = image_ratio(f"assets/bus/{color}_bus.png", 200)
    VEHICLE_IMAGES[("car", color, False)] = car
    VEHICLE_IMAGES[("car", color, True)] = pygame.transform.flip(
        car, True, False
    )  # flip(image, horizontal, vertical)
    VEHICLE_IMAGES[("bus", color, False)] = bus
    VEHICLE_IMAGES[("bus", color, True)] = pygame.transform.flip(bus, True, False)
VEHICLE_SIZES["car"] = VEHICLE_IMAGES[("car", "blue", False)].get_size()
VEHICLE_SIZES["bus"] = VEHICLE_IMAGES[("bus", "blue", False)].get_size()

# OTHER IMAGES
IMAGE_COIN = image_fixed("assets/coin.png", 24, 24)  # usual on the road
IMAGE_COIN_HEADS_UP_DISPLAY = image_fixed(
    "assets/coin.png", 40, 40
)  # head up display: shown in topbar
IMAGE_HEART = image_fixed("assets/heart.png", 40, 36)
IMAGE_HEARTBEAT = image_fixed("assets/heartbeat.png", 72, 72)
IMAGE_SHIELD = image_fixed("assets/shield.png", 44, 44)
IMAGE_HOSPITAL = image_ratio("assets/hospital.png", 350)


def handle_input_box(input_box, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        input_box.active = input_box.rect.collidepoint(event.pos)
    if event.type == pygame.KEYDOWN and input_box.active:
        if event.key == pygame.K_BACKSPACE:
            input_box.text = input_box.text[:-1]
        elif (
            event.key != pygame.K_RETURN
            and len(input_box.text) < 24
            and event.unicode.isprintable()
        ):
            input_box.text += event.unicode


def clear_input_box(input_box):
    input_box.text = ""


def draw_input_box(surface, input_box):
    pygame.draw.rect(
        surface,
        INPUT_ACTIVE if input_box.active else INPUT_BACKGROUND,
        input_box.rect,
        border_radius=8,
    )
    pygame.draw.rect(
        surface,
        BUTTON_COLOR if input_box.active else GRAY,
        input_box.rect,
        2,
        border_radius=8,
    )
    # label
    surface.blit(
        render_text(FONT_SMALL, input_box.label, LIGHT_GRAY),
        (input_box.rect.x, input_box.rect.y - 27),
    )
    # text
    disp = "*" * len(input_box.text) if input_box.is_password else input_box.text
    cur = "|" if input_box.active and pygame.time.get_ticks() % 1000 < 500 else ""
    surface.blit(
        render_text(FONT_SMALL, disp + cur, WHITE),
        (input_box.rect.x + 10, input_box.rect.y + 11),
    )


def draw_button(surface, rect, text, font, hover=False):
    pygame.draw.rect(
        surface, BUTTON_HOVER if hover else BUTTON_COLOR, rect, border_radius=10
    )
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
    t = render_text(font, text, WHITE)
    surface.blit(t, t.get_rect(center=rect.center))


def render_text_centered(font, text, color, surface, center_x, center_y):
    t = render_text(font, text, color)
    surface.blit(t, t.get_rect(center=(center_x, center_y)))


def draw_overlay(surface, rgba):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(rgba)
    surface.blit(overlay, (0, 0))


def enemy_update(enemy, scroll, delta_60):
    enemy.x -= (
        (scroll + enemy.speed)
        if enemy.lane == "upper"
        else max(1.5, scroll - enemy.speed)
    ) * delta_60


def enemy_draw(surface, enemy):
    surface.blit(
        VEHICLE_IMAGES[(enemy.vehicle_type, enemy.color, enemy.face_left)],
        (round(enemy.x), round(enemy.y)),
    )  # round prevent after images


def enemy_get_rect(enemy):
    return pygame.Rect(
        int(enemy.x) + 11, int(enemy.y) + 11, enemy.width - 22, enemy.height - 22
    )


def enemy_off_screen(enemy):
    return enemy.x < -260


def coin_update(coin_item, scroll, delta_60):
    coin_item.x -= scroll * delta_60


def coin_draw(surface, coin_item):
    if not coin_item.collected:
        surface.blit(
            IMAGE_COIN,
            IMAGE_COIN.get_rect(center=(round(coin_item.x), round(coin_item.y))),
        )


def coin_get_rect(coin_item):
    return pygame.Rect(int(coin_item.x) - 12, int(coin_item.y) - 12, 24, 24)


def coin_off_screen(coin_item):
    return coin_item.x < -30


def shield_update(shield_item, scroll, delta_60):
    shield_item.x -= scroll * delta_60


def shield_draw(surface, shield_item):
    if not shield_item.collected:
        surface.blit(
            IMAGE_SHIELD,
            IMAGE_SHIELD.get_rect(center=(round(shield_item.x), round(shield_item.y))),
        )


def shield_get_rect(shield_item):
    return pygame.Rect(
        int(shield_item.x) - shield_item.radius,
        int(shield_item.y) - shield_item.radius,
        shield_item.radius * 2,
        shield_item.radius * 2,
    )


def shield_off_screen(shield_item):
    return shield_item.x < -60


def house_update(house, scroll, delta_60):
    house.x -= scroll * delta_60


def house_off_screen(house):
    return house.x < -130


def house_draw(surface, house):
    x = round(house.x)
    y = ROAD_BOTTOM + 14 if house.row == 0 else ROAD_BOTTOM + 115
    body_color = HOUSE_BODY_COLORS[house.style]
    roof_color = HOUSE_ROOF_COLORS[house.style]
    pygame.draw.rect(surface, body_color, (x, y, 100, 90), border_radius=3)
    pygame.draw.rect(surface, BROWN, (x + 38, y + 55, 24, 35), border_radius=2)
    pygame.draw.circle(surface, WHITE, (x + 57, y + 72), 3)
    pygame.draw.rect(surface, (175, 225, 250), (x + 8, y + 18, 26, 20), border_radius=2)
    pygame.draw.rect(
        surface, (175, 225, 250), (x + 66, y + 18, 26, 20), border_radius=2
    )
    pygame.draw.polygon(surface, roof_color, [(x, y), (x + 50, y - 44), (x + 100, y)])


def player_update(player, delta):
    # Animate the ambulance at 15 FPS
    player.frame_timer += delta
    while player.frame_timer >= 1 / 15:  # every 1/15 second = ~66ms
        player.frame_timer -= 1 / 15
        player.frame = (player.frame + 1) % len(
            player.frames
        )  # loop back to 0 after last frame
        player.image = player.frames[player.frame]
    # Countdown shield duration, disable when expired
    if player.shield_timer > 0:
        player.shield_timer -= delta
        if player.shield_timer <= 0:
            player.shield_on = False
    # Countdown post-hit invincibility (2s blinking window)
    if player.invincibility_timer > 0:
        player.invincibility_timer -= delta


def player_activate_shield(player):
    player.shield_on = True
    player.shield_timer = 5


def player_get_rect(player):
    return pygame.Rect(
        int(player.x) + 25, int(player.y) + 25, player.width - 50, player.height - 50
    )


def player_draw(surface, player):
    if player.invincibility_timer > 0 and int(player.invincibility_timer * 8) % 2 == 0:
        return
    surface.blit(player.image, (round(player.x), round(player.y)))
    if player.shield_on:
        shield_ring = pygame.Surface((220, 150), pygame.SRCALPHA)
        cycle = pygame.time.get_ticks() % 600
        alpha = (
            60 + cycle * 140 // 600 if cycle < 300 else 200 - (cycle - 300) * 140 // 300
        )
        pygame.draw.ellipse(shield_ring, (100, 180, 255, alpha), (0, 0, 220, 150), 5)
        surface.blit(shield_ring, (round(player.x) - 10, round(player.y) - 10))


def hospital_draw(surface, hospital):
    surface.blit(IMAGE_HOSPITAL, (round(hospital.x), ROAD_BOTTOM + 100))


def draw_login(surface, input_username, input_password, error, mouse_position):
    surface.fill(UI_BACKGROUND)
    render_text_centered(FONT_TITLE, "Ambulance Surfer", WHITE, surface, 960, 185)
    render_text_centered(
        FONT_MEDIUM, "Sign in to continue", LIGHT_GRAY, surface, 960, 268
    )
    pygame.draw.line(surface, BUTTON_COLOR, (730, 318), (1190, 318), 2)
    draw_input_box(surface, input_username)
    draw_input_box(surface, input_password)
    draw_button(
        surface,
        RECT_LOGIN,
        "Log In",
        FONT_MEDIUM,
        RECT_LOGIN.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_CREATE,
        "Create New Account",
        FONT_MEDIUM,
        RECT_CREATE.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_FORGOT,
        "Forgot Password?",
        FONT_MEDIUM,
        RECT_FORGOT.collidepoint(mouse_position),
    )
    if error:
        render_text_centered(FONT_SMALL, error, RED, surface, 960, 862)


def draw_create(
    surface,
    create_acc_username,
    create_acc_password,
    create_acc_password_2,
    error,
    mouse_position,
):
    surface.fill(UI_BACKGROUND)
    render_text_centered(FONT_LARGE, "Create Account", WHITE, surface, 960, 250)
    draw_input_box(surface, create_acc_username)
    draw_input_box(surface, create_acc_password)
    draw_input_box(surface, create_acc_password_2)
    draw_button(
        surface,
        RECT_CREATE_ACCOUNT_OK,
        "Create Account",
        FONT_MEDIUM,
        RECT_CREATE_ACCOUNT_OK.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_CREATE_ACCOUNT_BACK,
        "Back to Login",
        FONT_MEDIUM,
        RECT_CREATE_ACCOUNT_BACK.collidepoint(mouse_position),
    )
    if error:
        render_text_centered(FONT_SMALL, error, RED, surface, 960, 682)


def draw_forgot(
    surface,
    forgot_pass_username,
    forgot_pass_password,
    forgot_pass_password_2,
    error,
    success_message,
    mouse_position,
):
    surface.fill(UI_BACKGROUND)
    render_text_centered(FONT_LARGE, "Reset Password", WHITE, surface, 960, 250)
    draw_input_box(surface, forgot_pass_username)
    draw_input_box(surface, forgot_pass_password)
    draw_input_box(surface, forgot_pass_password_2)
    draw_button(
        surface,
        RECT_FORGOT_PASSWORD_OK,
        "Change Password",
        FONT_MEDIUM,
        RECT_FORGOT_PASSWORD_OK.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_FORGOT_PASSWORD_BACK,
        "Back to Login",
        FONT_MEDIUM,
        RECT_FORGOT_PASSWORD_BACK.collidepoint(mouse_position),
    )
    if error:
        render_text_centered(FONT_SMALL, error, RED, surface, 960, 682)
    if success_message:
        render_text_centered(FONT_SMALL, success_message, GREEN, surface, 960, 682)


def draw_menu(surface, user, coin, fuel, mouse_position):
    surface.fill(UI_BACKGROUND)
    render_text_centered(FONT_TITLE, "AMBULANCE SURFER", WHITE, surface, 960, 172)
    pygame.draw.line(surface, BUTTON_COLOR, (640, 242), (1280, 242), 2)
    render_text_centered(
        FONT_MEDIUM, f"Welcome back, {user}!", YELLOW, surface, 960, 305
    )
    render_text_centered(
        FONT_MEDIUM, f"Your Coins: {coin}", COIN_COLOR, surface, 960, 368
    )
    render_text_centered(FONT_SMALL, f"Fuel: {fuel}", ORANGE, surface, 960, 410)
    draw_button(
        surface, RECT_START, "PLAY", FONT_LARGE, RECT_START.collidepoint(mouse_position)
    )
    draw_button(
        surface, RECT_SHOP, "SHOP", FONT_LARGE, RECT_SHOP.collidepoint(mouse_position)
    )
    draw_button(
        surface,
        RECT_LEADER,
        "LEADERBOARD",
        FONT_SMALL,
        RECT_LEADER.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_FRIENDS_BUTTON,
        "FRIENDS",
        FONT_SMALL,
        RECT_FRIENDS_BUTTON.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_LOGOUT,
        "Log Out",
        FONT_SMALL,
        RECT_LOGOUT.collidepoint(mouse_position),
    )
    for line_index, text_line in enumerate(
        [
            "How to Play",
            "Use UP / DOWN to change lane",
            "Press SHIFT to use 1 fuel  =  3 s of 2.5x speed",
            "Press CTRL to slow down",
            "Collect coins to buy skills and fuel",
            "Avoid matching your lane with incoming traffic!",
            "You only have 2 lives!",
        ]
    ):
        render_text_centered(
            FONT_SMALL, text_line, LIGHT_GRAY, surface, 960, 725 + line_index * 38
        )


def draw_ui_bar(surface, game_state, user, accounts, mouse_position):
    player = game_state.player

    # draw top bar rect
    pygame.draw.rect(surface, UI_BACKGROUND, (0, 0, 1920, TOPBAR_HEIGHT))

    # TIMELEFT
    surface.blit(
        IMAGE_HEARTBEAT, IMAGE_HEARTBEAT.get_rect(center=(62, TOPBAR_HEIGHT // 2))
    )
    seconds = max(0, int(game_state.time_left))  # prevent -0.3s
    timer_color = (
        GREEN
        if game_state.time_left > TIMER_SECONDS * 0.5
        else (ORANGE if game_state.time_left > TIMER_SECONDS * 0.25 else RED)
    )  # color of timer
    t = render_text(FONT_LARGE, f"{seconds}", timer_color)  # render seconds
    surface.blit(t, t.get_rect(midleft=(108, TOPBAR_HEIGHT // 2)))

    # COINS
    pygame.draw.rect(surface, UI_PANEL, RECT_COIN, border_radius=10)
    pygame.draw.rect(surface, COIN_COLOR, RECT_COIN, 2, border_radius=10)
    coin_center_x = RECT_COIN.x + 32
    coin_center_y = RECT_COIN.centery - 4
    surface.blit(
        IMAGE_COIN_HEADS_UP_DISPLAY,
        IMAGE_COIN_HEADS_UP_DISPLAY.get_rect(center=(coin_center_x, coin_center_y)),
    )
    t = render_text(FONT_LARGE, str(game_state.run_coin), COIN_COLOR)
    surface.blit(t, t.get_rect(midleft=(coin_center_x + 28, coin_center_y)))
    surface.blit(
        render_text(
            FONT_TINY,
            f"total  {accounts[user]["coin"]+game_state.run_coin}",
            LIGHT_GRAY,
        ),
        (RECT_COIN.x + 8, RECT_COIN.bottom - 18),
    )

    # LIVES
    for life_index in range(player.lives):
        surface.blit(
            IMAGE_HEART,
            IMAGE_HEART.get_rect(center=(482 + life_index * 52, TOPBAR_HEIGHT // 2)),
        )
    if player.shield_on:
        surface.blit(
            render_text(
                FONT_SMALL, f"SHIELD {player.shield_timer:.1f}", (150, 200, 255)
            ),
            (582, 90),
        )
    surface.blit(
        render_text(
            FONT_UI,
            f"FUEL: {game_state.fuel}",
            COIN_COLOR if game_state.fuel > 0 else LIGHT_GRAY,
        ),
        (582, 125),
    )
    if player.boost_timer > 0:
        surface.blit(
            render_text(FONT_SMALL, f"BOOST {player.boost_timer:.1f}", ORANGE),
            (582, 155),
        )
    progress = min(1, game_state.distance / WIN_DISTANCE)
    pygame.draw.rect(surface, UI_PANEL, RECT_PROGRESS, border_radius=8)
    if progress > 0:
        pygame.draw.rect(
            surface,
            (50, 200, 80),
            pygame.Rect(
                RECT_PROGRESS.x,
                RECT_PROGRESS.y,
                int(RECT_PROGRESS.w * progress),
                RECT_PROGRESS.h,
            ),
            border_radius=3,
        )
    pygame.draw.rect(surface, LIGHT_GRAY, RECT_PROGRESS, 2, border_radius=8)
    surface.blit(
        render_text(FONT_TINY, "HOSPITAL >>", WHITE),
        (RECT_PROGRESS.right + 8, RECT_PROGRESS.y + 3),
    )
    draw_button(
        surface,
        RECT_PAUSE,
        "II  Pause",
        FONT_SMALL,
        RECT_PAUSE.collidepoint(mouse_position),
    )


def draw_world(surface, game_state):
    pygame.draw.rect(surface, GREEN, (0, TOPBAR_HEIGHT, 1920, ROAD_TOP - TOPBAR_HEIGHT))
    pygame.draw.rect(surface, DARK_GREEN, (0, ROAD_BOTTOM, 1920, 1080 - ROAD_BOTTOM))
    pygame.draw.rect(surface, ROAD_COLOR, (0, ROAD_TOP, 1920, ROAD_HEIGHT))
    pygame.draw.rect(surface, WHITE, (0, ROAD_TOP, 1920, 5))
    pygame.draw.rect(surface, WHITE, (0, ROAD_BOTTOM - 5, 1920, 5))
    rounded_offset = round(game_state.line_offset)
    for x_position in range(-200, 2120, 200):
        pygame.draw.rect(
            surface, YELLOW, (x_position + rounded_offset, DIVIDER_Y - 2, 90, 4)
        )
    for house in game_state.houses:
        house_draw(surface, house)
    for coin_item in game_state.coins:
        coin_draw(surface, coin_item)
    for shield_item in game_state.shields:
        shield_draw(surface, shield_item)
    for enemy in game_state.enemies:
        enemy_draw(surface, enemy)

    if game_state.hospital:
        hospital_draw(surface, game_state.hospital)

    player_draw(surface, game_state.player)


def draw_pause_overlay(surface, mouse_position):
    draw_overlay(surface, (0, 0, 0, 165))
    render_text_centered(FONT_TITLE, "PAUSED", WHITE, surface, 960, 355)
    draw_button(
        surface,
        RECT_RESUME,
        "Resume",
        FONT_MEDIUM,
        RECT_RESUME.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_PAUSE_SAVE,
        "Main Menu",
        FONT_MEDIUM,
        RECT_PAUSE_SAVE.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_PAUSE_QUIT,
        "Quit Game",
        FONT_MEDIUM,
        RECT_PAUSE_QUIT.collidepoint(mouse_position),
    )


def draw_end(
    surface,
    mouse_position,
    background,
    colorized,
    headline,
    headline_color,
    subtitle,
    subtitle_color,
    coin,
):
    surface.fill(background)
    draw_overlay(surface, colorized)
    render_text_centered(FONT_TITLE, headline, headline_color, surface, 960, 405)
    render_text_centered(FONT_MEDIUM, subtitle, subtitle_color, surface, 960, 488)
    render_text_centered(
        FONT_SMALL,
        f"Coins earned this run: {coin}",
        COIN_COLOR,
        surface,
        960,
        550,
    )
    draw_button(
        surface,
        RECT_RETRY,
        "Try Again",
        FONT_MEDIUM,
        RECT_RETRY.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_GAME_MENU,
        "Main Menu",
        FONT_MEDIUM,
        RECT_GAME_MENU.collidepoint(mouse_position),
    )


def draw_dead_time(surface, coin, mouse_position):
    draw_end(
        surface,
        mouse_position,
        (14, 6, 6),
        (180, 0, 0, 55),
        "The patient has died.",
        RED,
        "You ran out of time...  You failed.",
        (255, 160, 160),
        coin,
    )


def draw_dead_crash(surface, coin, mouse_position):
    draw_end(
        surface,
        mouse_position,
        (10, 8, 4),
        (200, 100, 0, 55),
        "Oh no, you crashed!",
        ORANGE,
        "The ambulance is totalled. Run failed.",
        (255, 200, 130),
        coin,
    )


def draw_win(surface, coin, mouse_position):
    draw_end(
        surface,
        mouse_position,
        (4, 14, 4),
        (0, 200, 50, 55),
        "PATIENT SAVED!",
        GREEN,
        "You reached the hospital in time!",
        (180, 255, 180),
        coin,
    )


def fuel_card_rects(pack_index):
    card_x = 510 + pack_index * 310
    card_y = 440
    return pygame.Rect(card_x, card_y, 280, 180), pygame.Rect(
        card_x + 50, card_y + 130, 180, 40
    )


def draw_shop(surface, user, accounts, mouse_position, message):
    surface.fill(UI_BACKGROUND)
    render_text_centered(FONT_TITLE, "SHOP", COIN_COLOR, surface, CENTER_X, 120)
    render_text_centered(
        FONT_MEDIUM,
        f"Your Coins: {accounts[user]["coin"]}",
        COIN_COLOR,
        surface,
        CENTER_X,
        185,
    )
    draw_shop_fuel(
        surface, accounts[user].get("fuel", 0), accounts[user]["coin"], mouse_position
    )
    if message:
        render_text_centered(FONT_MEDIUM, message, GREEN, surface, 960, 920)
    draw_button(
        surface,
        RECT_SHOP_BACK,
        "Back to Menu",
        FONT_MEDIUM,
        RECT_SHOP_BACK.collidepoint(mouse_position),
    )


def draw_shop_fuel(surface, fuel, coin, mouse_position):
    render_text_centered(FONT_LARGE, f"Current Fuel: {fuel}", WHITE, surface, 960, 340)
    render_text_centered(
        FONT_SMALL,
        "Press SHIFT in-game to use 1 fuel  =  3 s of 2.5x speed",
        LIGHT_GRAY,
        surface,
        960,
        390,
    )
    for pack_index, pack in enumerate(FUEL_PACKS):
        card_rect, buy_rect = fuel_card_rects(pack_index)
        pygame.draw.rect(surface, UI_PANEL, card_rect, border_radius=12)
        pygame.draw.rect(surface, LIGHT_GRAY, card_rect, 2, border_radius=12)
        render_text_centered(
            FONT_LARGE,
            pack["label"],
            WHITE,
            surface,
            card_rect.centerx,
            card_rect.y + 45,
        )
        render_text_centered(
            FONT_MEDIUM,
            f"{pack["cost"]} coins",
            COIN_COLOR,
            surface,
            card_rect.centerx,
            card_rect.y + 95,
        )
        if coin >= pack["cost"]:
            draw_button(
                surface,
                buy_rect,
                "BUY",
                FONT_SMALL,
                buy_rect.collidepoint(mouse_position),
            )
        else:
            pygame.draw.rect(surface, GRAY, buy_rect, border_radius=10)
            pygame.draw.rect(surface, LIGHT_GRAY, buy_rect, 2, border_radius=10)
            render_text_centered(
                FONT_SMALL,
                "Can't Afford",
                LIGHT_GRAY,
                surface,
                buy_rect.centerx,
                buy_rect.centery,
            )


#  Leaderboard + Achievements screen
def draw_leaderboard(surface, user, accounts, mouse_position):
    surface.fill(UI_BACKGROUND)
    render_text_centered(
        FONT_TITLE, "LEADERBOARD & ACHIEVEMENTS", COIN_COLOR, surface, 960, 75
    )
    pygame.draw.line(surface, BUTTON_COLOR, (60, 140), (1860, 140), 2)

    #  Left panel: Global Rankings sorted by total_coin descending
    ranked = sorted(
        accounts.items(),
        key=lambda key_value: key_value[1].get("total_coin", 0),
        reverse=True,
    )

    render_text_centered(FONT_MEDIUM, "Global Rankings", WHITE, surface, 380, 175)
    pygame.draw.line(surface, LIGHT_GRAY, (60, 200), (710, 200), 1)

    column_x = {"rank": 80, "name": 185, "coin": 470, "wins": 630}
    for label, x in [
        ("Rank", column_x["rank"]),
        ("Player", column_x["name"]),
        ("Total Coins", column_x["coin"]),
        ("Wins", column_x["wins"]),
    ]:
        surface.blit(render_text(FONT_SMALL, label, COIN_COLOR), (x, 207))
    pygame.draw.line(surface, LIGHT_GRAY, (60, 234), (710, 234), 1)

    MEDAL = {1: COIN_COLOR, 2: (192, 192, 192), 3: (205, 127, 50)}
    for rank, (username, data) in enumerate(ranked, 1):
        y = 244 + (rank - 1) * 50
        if y > SCREEN_HEIGHT - 280:
            break
        is_me = username == user
        row_background = (45, 45, 95) if is_me else (26, 26, 52)
        name_color = YELLOW if is_me else WHITE
        pygame.draw.rect(surface, row_background, (65, y - 4, 645, 42), border_radius=6)
        if is_me:
            pygame.draw.rect(
                surface, BUTTON_COLOR, (65, y - 4, 645, 42), 2, border_radius=6
            )
        medal_color = MEDAL.get(rank, LIGHT_GRAY)
        surface.blit(
            render_text(FONT_SMALL, f"#{rank}", medal_color), (column_x["rank"], y + 6)
        )
        surface.blit(
            render_text(FONT_SMALL, username, name_color), (column_x["name"], y + 6)
        )
        surface.blit(
            render_text(FONT_SMALL, str(data.get("total_coin", 0)), COIN_COLOR),
            (column_x["coin"], y + 6),
        )
        surface.blit(
            render_text(FONT_SMALL, str(data.get("wins", 0)), WHITE),
            (column_x["wins"], y + 6),
        )

    # ── Right panel: Personal Achievements ──
    achievements_x = 760
    user_data = accounts[user]
    unlocked = sum(
        1 for achievement_entry in ACHIEVEMENTS if achievement_entry["check"](user_data)
    )
    render_text_centered(
        FONT_MEDIUM,
        f"{user}'s Achievements",
        WHITE,
        surface,
        achievements_x + (SCREEN_WIDTH - 60 - achievements_x) // 2,
        175,
    )
    pygame.draw.line(
        surface, LIGHT_GRAY, (achievements_x, 200), (SCREEN_WIDTH - 60, 200), 1
    )
    surface.blit(
        render_text(
            FONT_SMALL, f"{unlocked} / {len(ACHIEVEMENTS)} unlocked", COIN_COLOR
        ),
        (achievements_x + 8, 207),
    )
    pygame.draw.line(
        surface, LIGHT_GRAY, (achievements_x, 234), (SCREEN_WIDTH - 60, 234), 1
    )

    for i, achievement in enumerate(ACHIEVEMENTS):
        y = 244 + i * 72
        done = achievement["check"](user_data)
        background = (28, 72, 28) if done else (32, 32, 58)
        border_color = GREEN if done else GRAY
        pygame.draw.rect(
            surface,
            background,
            (achievements_x, y - 4, SCREEN_WIDTH - 70 - achievements_x, 62),
            border_radius=8,
        )
        pygame.draw.rect(
            surface,
            border_color,
            (achievements_x, y - 4, SCREEN_WIDTH - 70 - achievements_x, 62),
            2,
            border_radius=8,
        )
        mark = "+" if done else "o"  # ASCII safe
        mark_color = GREEN if done else LIGHT_GRAY
        surface.blit(
            render_text(FONT_MEDIUM, mark, mark_color), (achievements_x + 12, y + 3)
        )
        surface.blit(
            render_text(FONT_SMALL, achievement["name"], WHITE if done else LIGHT_GRAY),
            (achievements_x + 52, y + 3),
        )
        surface.blit(
            render_text(FONT_TINY, achievement["desc"], LIGHT_GRAY),
            (achievements_x + 52, y + 30),
        )

    draw_button(
        surface,
        RECT_LEADERBOARD_BACK,
        "Back to Menu",
        FONT_MEDIUM,
        RECT_LEADERBOARD_BACK.collidepoint(mouse_position),
    )


#  Friends screen
def draw_friends(
    surface,
    user,
    accounts,
    friends_input_box,
    friends_result,
    friends_scroll,
    mouse_position,
):
    surface.fill(UI_BACKGROUND)
    render_text_centered(FONT_TITLE, "FRIENDS", COIN_COLOR, surface, CENTER_X, 75)
    pygame.draw.line(surface, BUTTON_COLOR, (60, 140), (SCREEN_WIDTH - 60, 140), 2)

    friends = accounts[user].get("friends", [])  # already sorted

    # Left panel: friends list
    render_text_centered(
        FONT_MEDIUM, f"Your Friends  ({len(friends)})", WHITE, surface, 370, 175
    )
    pygame.draw.line(surface, LIGHT_GRAY, (60, 200), (700, 200), 1)

    if not friends:
        surface.blit(
            render_text(FONT_SMALL, "No friends yet — add some!", LIGHT_GRAY), (80, 240)
        )
    else:
        MAX_VIS = 10  # max visible friends
        start = friends_scroll
        end = min(start + MAX_VIS, len(friends))
        for index in range(start, end):
            friend_name = friends[index]
            row_y = 210 + (index - start) * 50
            row_background = (40, 40, 82) if index % 2 == 0 else (28, 28, 55)
            pygame.draw.rect(
                surface, row_background, (65, row_y, 620, 42), border_radius=6
            )
            surface.blit(
                render_text(FONT_SMALL, f"{index+1}.  {friend_name}", WHITE),
                (85, row_y + 8),
            )
            if friend_name in accounts:
                total_coins = accounts[friend_name].get("total_coin", 0)
                wins = accounts[friend_name].get("wins", 0)
                surface.blit(
                    render_text(
                        FONT_TINY, f"Coins: {total_coins}  |  Wins: {wins}", COIN_COLOR
                    ),
                    (490, row_y + 12),
                )
        if friends_scroll > 0:
            surface.blit(
                render_text(FONT_TINY, "^ UP arrow to scroll", LIGHT_GRAY), (260, 197)
            )
        if end < len(friends):
            surface.blit(
                render_text(FONT_TINY, "v DOWN arrow to scroll", LIGHT_GRAY),
                (260, 210 + MAX_VIS * 50 + 4),
            )

    # Right panel: Search / Add / Remove
    right_panel_x = 760
    render_text_centered(
        FONT_MEDIUM,
        "Search  /  Manage",
        WHITE,
        surface,
        right_panel_x + (SCREEN_WIDTH - 60 - right_panel_x) // 2,
        175,
    )
    pygame.draw.line(
        surface, LIGHT_GRAY, (right_panel_x, 200), (SCREEN_WIDTH - 60, 200), 1
    )

    surface.blit(
        render_text(FONT_SMALL, "Enter a username:", LIGHT_GRAY), (right_panel_x, 332)
    )
    draw_input_box(surface, friends_input_box)
    draw_button(
        surface,
        RECT_FRIENDS_FIND,
        "Find",
        FONT_SMALL,
        RECT_FRIENDS_FIND.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_FRIENDS_ADD,
        "Add",
        FONT_SMALL,
        RECT_FRIENDS_ADD.collidepoint(mouse_position),
    )
    draw_button(
        surface,
        RECT_FRIENDS_REMOVE,
        "Remove",
        FONT_SMALL,
        RECT_FRIENDS_REMOVE.collidepoint(mouse_position),
    )

    if friends_result:
        is_success = friends_result.startswith("Added") or friends_result.startswith(
            "Found"
        )
        is_error = (
            "not found" in friends_result.lower()
            or "can't" in friends_result.lower()
            or "not in" in friends_result.lower()
        )
        result_color = GREEN if is_success else (RED if is_error else LIGHT_GRAY)
        surface.blit(
            render_text(FONT_SMALL, friends_result, result_color), (right_panel_x, 510)
        )

    draw_button(
        surface,
        RECT_FRIENDS_BACK,
        "Back to Menu",
        FONT_MEDIUM,
        RECT_FRIENDS_BACK.collidepoint(mouse_position),
    )


# Update game


def update_game(game_state, delta, accounts, user):
    player = game_state.player
    keys = pygame.key.get_pressed()
    if player.boost_timer > 0:
        player.boost_timer -= delta
        target = 2.5
    elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
        target = 0.5
    else:
        target = 1
    player.boost += (target - player.boost) * 10 * delta
    boost = player.boost
    speed = PLAYER_SPEED * boost
    if keys[pygame.K_UP]:
        player.y -= speed * delta
    if keys[pygame.K_DOWN]:
        player.y += speed * delta
    player.y = max(
        float(ROAD_TOP + 5), min(player.y, float(ROAD_BOTTOM - player.height - 5))
    )
    player_update(player, delta)

    game_state.time_left -= delta
    if game_state.time_left <= 0:
        accounts[user]["coin"] += game_state.run_coin
        accounts[user]["fuel"] = game_state.fuel
        #  track lifetime gold on failure too
        accounts[user]["total_coin"] = (
            accounts[user].get("total_coin", 0) + game_state.run_coin
        )
        save_accounts(accounts)
        return STATE_DEAD_TIME

    delta_60 = delta * 60
    game_state.distance += game_state.scroll * boost * delta_60
    game_state.scroll = SCROLL_BASE + game_state.distance / 9000

    if game_state.distance >= WIN_DISTANCE:
        if game_state.hospital is None:
            game_state.hospital = Hospital()

        game_state.hospital.x -= game_state.scroll * boost * delta_60

        if game_state.hospital.x <= game_state.player.x + 60:
            accounts[user]["coin"] += game_state.run_coin
            accounts[user]["fuel"] = game_state.fuel
            #  track wins and lifetime gold on victory
            accounts[user]["wins"] = accounts[user].get("wins", 0) + 1
            accounts[user]["total_coin"] = (
                accounts[user].get("total_coin", 0) + game_state.run_coin
            )
            save_accounts(accounts)
            return STATE_WIN

    scroll = game_state.scroll * boost
    game_state.line_offset = (game_state.line_offset - scroll * delta_60) % 200

    game_state.enemy_spawn_timer -= delta
    if game_state.enemy_spawn_timer <= 0:
        lane = random.choices(["upper", "lower"], weights=[6, 4])[0]
        game_state.enemies.append(Enemy(lane, VEHICLE_SIZES))
        game_state.enemy_spawn_timer = random.uniform(1.2, 3.2)
    for enemy in game_state.enemies:
        enemy_update(enemy, scroll, delta_60)
    game_state.enemies = [
        enemy for enemy in game_state.enemies if not enemy_off_screen(enemy)
    ]

    game_state.coin_spawn_timer -= delta
    if game_state.coin_spawn_timer <= 0:
        game_state.coins.append(Coin())
        game_state.coin_spawn_timer = random.uniform(0.7, 2)
    player_rect = player_get_rect(player)
    for coin_item in game_state.coins:
        coin_update(coin_item, scroll, delta_60)
        if not coin_item.collected and coin_get_rect(coin_item).colliderect(
            player_rect
        ):
            coin_item.collected = True
            game_state.run_coin += 1
    game_state.coins = [
        coin_item for coin_item in game_state.coins if not coin_off_screen(coin_item)
    ]

    game_state.shield_spawn_timer -= delta
    if game_state.shield_spawn_timer <= 0:
        game_state.shields.append(Shield_on_road())
        game_state.shield_spawn_timer = random.uniform(9, 18)
    for shield_item in game_state.shields:
        shield_update(shield_item, scroll, delta_60)
        if not shield_item.collected and shield_get_rect(shield_item).colliderect(
            player_rect
        ):
            shield_item.collected = True
            player_activate_shield(player)
    game_state.shields = [
        shield_item
        for shield_item in game_state.shields
        if not shield_off_screen(shield_item)
    ]

    game_state.house_spawn_timer -= delta
    if game_state.house_spawn_timer <= 0:
        game_state.houses.append(House())
        game_state.house_spawn_timer = random.uniform(1.5, 4.2)
    for house in game_state.houses:
        house_update(house, scroll, delta_60)
    game_state.houses = [
        house for house in game_state.houses if not house_off_screen(house)
    ]

    if player.invincibility_timer <= 0 and not player.shield_on:
        for enemy in game_state.enemies:
            if enemy_get_rect(enemy).colliderect(player_rect):
                player.lives -= 1
                player.invincibility_timer = 2
                game_state.enemies.remove(enemy)
                if player.lives <= 0:
                    accounts[user]["coin"] += game_state.run_coin
                    accounts[user]["fuel"] = game_state.fuel
                    #  track lifetime gold on crash
                    accounts[user]["total_coin"] = (
                        accounts[user].get("total_coin", 0) + game_state.run_coin
                    )
                    save_accounts(accounts)
                    return STATE_DEAD_CRASH
                break
    return None
