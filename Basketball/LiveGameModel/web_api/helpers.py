def infer_state(game_desc):
    """ Returns before if the game hasn't started,
        during if it is currently being played,
        and over if its over. """
    if " at " in game_desc:
        return "before"
    elif "^" in game_desc:
        return "over"
    else:
        return "during"
