import json
from essence.constants import *
from essence.classes import *


def load_accounts():
    accounts = {}
    with open(ACCOUNT_FILE) as file:
        for player_data in json.load(file):
            accounts[player_data["Name"]] = {
                "password": player_data["PW"],
                "coin": player_data.get("Coin", 0),
                "fuel": player_data.get("Fuel", 0),
                "wins": player_data.get("Wins", 0),
                "total_coin": player_data.get("TotalCoin", 0),
                "friends": player_data.get("Friends", []),
            }
    return accounts


def save_accounts(accounts):
    with open(ACCOUNT_FILE, "w") as file:
        json.dump(
            [
                {
                    "Name": username,
                    "PW": data["password"],
                    "Coin": data["coin"],
                    "Fuel": data.get("fuel", 0),
                    "Wins": data.get("wins", 0),
                    "TotalCoin": data.get("total_coin", 0),
                    "Friends": data.get("friends", []),
                }
                for username, data in accounts.items()
            ],
            file,
            indent=4,
        )


def new_game(accounts, user):
    from essence.draw import PLAYER_FRAMES

    fuel = accounts[user].get("fuel", 0)  # get fuel, if not found, return 0
    return Game_state(fuel, PLAYER_FRAMES)


# Friends system


def binary_search_friends(friends_list, name):
    min, max = 0, len(friends_list) - 1
    while min <= max:
        mid = (min + max) // 2
        if friends_list[mid] == name:
            return mid
        elif friends_list[mid] < name:
            min = mid + 1
        else:
            max = mid - 1
    return -1


def add_friend(accounts, user, target):
    # Add target to user's friends list, keeping the list sorted for binary search.
    if not target:
        return "Please enter a username."
    if target not in accounts:
        return f"User '{target}' not found."
    if target == user:
        return "You can't add yourself!"
    friends = accounts[user].get("friends", [])
    if binary_search_friends(friends, target) != -1:
        return f"'{target}' is already your friend."
    friends.append(target)
    friends.sort()  # keep sorted so binary search stays valid
    accounts[user]["friends"] = friends
    save_accounts(accounts)
    return f"Added '{target}' as a friend!"


def remove_friend(accounts, user, target):
    # Remove target from user's friends list using binary search to locate them.
    if not target:
        return "Please enter a username."
    friends = accounts[user].get("friends", [])
    target_index = binary_search_friends(friends, target)
    if target_index == -1:
        return f"'{target}' is not in your friends list."
    friends.pop(target_index)
    accounts[user]["friends"] = friends
    save_accounts(accounts)
    return f"Removed '{target}' from friends."
