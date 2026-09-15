import pygame
import random
import json
from pygame import mixer
from essence.constants import *
from essence.classes import *

pygame.init()
pygame.key.set_repeat(300, 50) #if hold a key, it will repeat every 50ms after 300ms delay


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
game_clock = pygame.time.Clock()
pygame.display.set_caption("Ambulance Surfer")

from essence.draw import *
from essence.acc_handle import *


def main():
    accounts = load_accounts()
    current_user = None
    state = STATE_LOGIN

    input_box_username = Input_box(795, 468, 330, 50, "Username")
    input_box_password = Input_box(795, 568, 330, 50, "Password", is_password=True)
    create_acc_username = Input_box(795, 410, 330, 50, "Username")
    create_acc_password = Input_box(795, 510, 330, 50, "Password", is_password=True)
    create_acc_password_2 = Input_box(
        795, 610, 330, 50, "Confirm Password", is_password=True
    )
    forgot_pass_username = Input_box(795, 410, 330, 50, "Username")
    forgot_pass_password = Input_box(795, 510, 330, 50, "New Password", is_password=True)
    forgot_pass_password_2 = Input_box(
        795, 610, 330, 50, "Confirm Password", is_password=True
    )
    login_error = create_account_error = forgot_password_error = (
        forgot_password_success
    ) = ""

    game_state = Game_state(0, PLAYER_FRAMES)
    delta = 0
    shop_message = ""
    shop_message_timer = 0

    friends_input_box = Input_box(760, 373, 350, 46, "Username")
    friends_message = ""
    friends_scroll = 0

    while True:
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if current_user:
                    save_accounts(accounts)
                pygame.quit()
                raise SystemExit

            if state == STATE_LOGIN:
                handle_input_box(input_box_username, event)
                handle_input_box(input_box_password, event)
                if (event.type == pygame.MOUSEBUTTONDOWN and RECT_LOGIN.collidepoint(event.pos)) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    username, password = input_box_username.text.strip(), input_box_password.text.strip()                    
                    if username in accounts and accounts[username]["password"] == password:
                        current_user = username
                        login_error = ""
                        state = STATE_MENU
                    else:
                        login_error = "Incorrect username or password."
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RECT_CREATE.collidepoint(event.pos):
                        state = STATE_CREATE
                    if RECT_FORGOT.collidepoint(event.pos):
                        state = STATE_FORGOT

            elif state == STATE_CREATE:
                handle_input_box(create_acc_username, event)
                handle_input_box(create_acc_password, event)
                handle_input_box(create_acc_password_2, event)
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and RECT_CREATE_ACCOUNT_OK.collidepoint(event.pos)
                ):
                    username, password, password_confirm = (
                        create_acc_username.text.strip(),
                        create_acc_password.text.strip(),
                        create_acc_password_2.text.strip(),
                    )
                    if not username or not password:
                        create_account_error = "All fields are required."
                    elif username in accounts:
                        create_account_error = "Username already taken."
                    elif password != password_confirm:
                        create_account_error = "Passwords do not match."
                    elif len(password) < 4:
                        create_account_error = "Password must be at least 4 characters."
                    else:
                        accounts[username] = {
                            "password": password,
                            "coin": 0,
                            "fuel": 0,
                            "wins": 0,
                            "total_coin": 0,
                            "friends": [],
                        }
                        save_accounts(accounts)
                        clear_input_box(create_acc_username)
                        clear_input_box(create_acc_password)
                        clear_input_box(create_acc_password_2)
                        create_account_error = ""
                        state = STATE_LOGIN
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and RECT_CREATE_ACCOUNT_BACK.collidepoint(event.pos)
                ):
                    state = STATE_LOGIN

            elif state == STATE_FORGOT:
                handle_input_box(forgot_pass_username, event)
                handle_input_box(forgot_pass_password, event)
                handle_input_box(forgot_pass_password_2, event)
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and RECT_FORGOT_PASSWORD_OK.collidepoint(event.pos)
                ):
                    username, password, password_confirm = (
                        forgot_pass_username.text.strip(),
                        forgot_pass_password.text.strip(),
                        forgot_pass_password_2.text.strip(),
                    )
                    if username not in accounts:
                        forgot_password_error = "Username not found."
                        forgot_password_success = ""
                    elif password != password_confirm:
                        forgot_password_error = "Passwords do not match."
                        forgot_password_success = ""
                    elif len(password) < 4:
                        forgot_password_error = "Password too short."
                        forgot_password_success = ""
                    else:
                        accounts[username]["password"] = password
                        save_accounts(accounts)
                        clear_input_box(forgot_pass_username)
                        clear_input_box(forgot_pass_password)
                        clear_input_box(forgot_pass_password_2)
                        forgot_password_error = ""
                        forgot_password_success = "Password updated! Please log in."
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and RECT_FORGOT_PASSWORD_BACK.collidepoint(event.pos)
                ):
                    state = STATE_LOGIN
                    forgot_password_error = forgot_password_success = ""

            elif state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RECT_START.collidepoint(event.pos):
                        game_state = new_game(accounts, current_user)
                        state = STATE_PLAY
                        pygame.mixer.music.load("assets/sound/ambulance.mp3")
                        pygame.mixer.music.play(-1)
                        pygame.mixer.Sound("assets/sound/traffic.mp3").play(-1)
                    elif RECT_SHOP.collidepoint(event.pos):
                        shop_message = ""
                        state = STATE_SHOP
                    elif RECT_LEADER.collidepoint(event.pos):
                        state = STATE_LEADERBOARD
                    elif RECT_FRIENDS_BUTTON.collidepoint(event.pos):
                        friends_message = ""
                        clear_input_box(friends_input_box)
                        friends_scroll = 0
                        state = STATE_FRIENDS
                    elif RECT_LOGOUT.collidepoint(event.pos):
                        current_user = None
                        clear_input_box(input_box_username)
                        clear_input_box(input_box_password)
                        state = STATE_LOGIN

            elif state == STATE_PLAY:
                if event.type == pygame.MOUSEBUTTONDOWN and RECT_PAUSE.collidepoint(
                    event.pos
                ):
                    state = STATE_PAUSE
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = STATE_PAUSE
                    if (
                        event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT)
                        and game_state.fuel > 0
                        and game_state.player.boost_timer <= 0
                    ):
                        game_state.fuel -= 1
                        game_state.player.boost_timer = BOOST_DURATION

            elif state == STATE_PAUSE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RECT_RESUME.collidepoint(event.pos):
                        state = STATE_PLAY
                    elif RECT_PAUSE_SAVE.collidepoint(event.pos):
                        accounts[current_user]["coin"] += game_state.run_coin
                        accounts[current_user]["fuel"] = game_state.fuel
                        save_accounts(accounts)
                        state = STATE_MENU
                        pygame.mixer.music.stop()
                        pygame.mixer.stop()
                    elif RECT_PAUSE_QUIT.collidepoint(event.pos):
                        accounts[current_user]["coin"] += game_state.run_coin
                        accounts[current_user]["fuel"] = game_state.fuel
                        save_accounts(accounts)
                        pygame.quit()
                        raise SystemExit

            elif state in (STATE_DEAD_TIME, STATE_DEAD_CRASH, STATE_WIN):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RECT_RETRY.collidepoint(event.pos):
                        game_state = new_game(accounts, current_user)
                        state = STATE_PLAY
                        pygame.mixer.music.load("assets/sound/ambulance.mp3")
                        pygame.mixer.music.play(-1)
                        pygame.mixer.Sound("assets/sound/traffic.mp3").play(-1)
                    elif RECT_GAME_MENU.collidepoint(event.pos):
                        state = STATE_MENU
                        pygame.mixer.music.stop()
                        pygame.mixer.stop()

            elif state == STATE_SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RECT_SHOP_BACK.collidepoint(event.pos):
                        state = STATE_MENU
                        shop_message = ""
                    else:
                        for i, pack in enumerate(FUEL_PACKS):
                            _, buy_rect = fuel_card_rects(i)
                            if (
                                buy_rect.collidepoint(event.pos)
                                and accounts[current_user]["coin"] >= pack["cost"]
                            ):
                                accounts[current_user]["coin"] -= pack["cost"]
                                accounts[current_user]["fuel"] = (
                                    accounts[current_user].get("fuel", 0)
                                    + pack["amount"]
                                )
                                save_accounts(accounts)
                                shop_message = f"Bought {pack["label"]}!"
                                shop_message_timer = 2
                                break

            # Leaderboard events
            elif state == STATE_LEADERBOARD:
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and RECT_LEADERBOARD_BACK.collidepoint(event.pos)
                ):
                    state = STATE_MENU

            # Friends events
            elif state == STATE_FRIENDS:
                handle_input_box(friends_input_box, event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        friends_scroll = max(0, friends_scroll - 1)
                    elif event.key == pygame.K_DOWN:
                        max_scroll = max(
                            0, len(accounts[current_user].get("friends", [])) - 10
                        )
                        friends_scroll = min(max_scroll, friends_scroll + 1)
                if event.type == pygame.MOUSEWHEEL:
                    friends_scroll -= event.y
                    friends_scroll = max(
                        0,
                        min(
                            friends_scroll,
                            max(0, len(accounts[current_user].get("friends", [])) - 10),
                        ),
                    )
                if event.type == pygame.MOUSEBUTTONDOWN:
                    target = friends_input_box.text.strip()
                    if RECT_FRIENDS_FIND.collidepoint(event.pos):
                        # Binary search the sorted friends list and report position
                        friends = accounts[current_user].get("friends", [])
                        index = binary_search_friends(friends, target)
                        if index != -1:
                            friends_message = (
                                f"Found '{target}' — position {index+1} in your list."
                            )
                        else:
                            friends_message = f"'{target}' is not in your friends list."
                    elif RECT_FRIENDS_ADD.collidepoint(event.pos):
                        friends_message = add_friend(accounts, current_user, target)
                        friends_scroll = 0
                    elif RECT_FRIENDS_REMOVE.collidepoint(event.pos):
                        friends_message = remove_friend(accounts, current_user, target)
                        friends_scroll = 0
                    elif RECT_FRIENDS_BACK.collidepoint(event.pos):
                        state = STATE_MENU
                        friends_message = ""
                        clear_input_box(friends_input_box)

        if state == STATE_PLAY:
            result = update_game(game_state, delta, accounts, current_user)
            if result:
                state = result
                if state in (STATE_DEAD_CRASH, STATE_DEAD_TIME, STATE_WIN):
                    pygame.mixer.music.stop()
                    pygame.mixer.stop()
                if state == STATE_DEAD_CRASH:
                    pygame.mixer.Sound("assets/sound/crash.mp3").play()
                elif state == STATE_DEAD_TIME:
                    pygame.mixer.Sound("assets/sound/death.mp3").play()

        if shop_message_timer > 0:
            shop_message_timer -= delta
            if shop_message_timer <= 0:
                shop_message = ""

        # Draw current state
        if state == STATE_LOGIN:
            draw_login(
                screen, input_box_username, input_box_password, login_error, mouse
            )
        elif state == STATE_CREATE:
            draw_create(
                screen,
                create_acc_username,
                create_acc_password,
                create_acc_password_2,
                create_account_error,
                mouse,
            )
        elif state == STATE_FORGOT:
            draw_forgot(
                screen,
                forgot_pass_username,
                forgot_pass_password,
                forgot_pass_password_2,
                forgot_password_error,
                forgot_password_success,
                mouse,
            )
        elif state == STATE_MENU:
            draw_menu(
                screen,
                current_user,
                accounts[current_user]["coin"],
                accounts[current_user].get("fuel", 0),
                mouse,
            )
        elif state in (STATE_PLAY, STATE_PAUSE):
            draw_ui_bar(screen, game_state, current_user, accounts, mouse)
            draw_world(screen, game_state)
            if state == STATE_PAUSE:
                draw_pause_overlay(screen, mouse)
        elif state == STATE_DEAD_TIME:
            draw_dead_time(screen, game_state.run_coin, mouse)
        elif state == STATE_DEAD_CRASH:
            draw_dead_crash(screen, game_state.run_coin, mouse)
        elif state == STATE_WIN:
            draw_win(screen, game_state.run_coin, mouse)
        elif state == STATE_SHOP:
            draw_shop(screen, current_user, accounts, mouse, shop_message)
        elif state == STATE_LEADERBOARD:
            draw_leaderboard(screen, current_user, accounts, mouse)
        elif state == STATE_FRIENDS:
            draw_friends(
                screen,
                current_user,
                accounts,
                friends_input_box,
                friends_message,
                friends_scroll,
                mouse,
            )

        pygame.display.flip()
        delta = game_clock.tick(60) / 1000


if __name__ == "__main__":
    main()
