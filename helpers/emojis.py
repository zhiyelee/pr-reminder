import random
EMOJI_LIST = [
    ':horse:',
    ':dog:',
    ':monkey:',
    ':deer:',
    ':cat:',
    ':rooster:',
    ':eagle:',
    ':lemon:',
    ':ramen:',
    ':cake:',
]

NAMES_EMOJI = {
    'upside_down_face': ':upside_down_face:',
    'passenger_ship': ':passenger_ship:'
}

"""
get random emoji from the EMOJI_LIST
"""
def get_random_emoji():
    return random.choice(EMOJI_LIST)
