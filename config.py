import json


class Config:
    def __init__(self):
        with open("config.json") as file:
            data = json.load(file)
            game = data["game"]
            self.x_offset = game.get("x_offset", 16)
            self.y_offset = game.get("y_offset", 16)
            self.tile_size = game.get("tile_size", 64)
            self.rim_size = game.get("rim_size", 2)
            self.panel_width = game.get("panel_width", 600)
            self.font = game.get("font", "Noto Mono")

            bot = data["bot"]
            self.threading = bot.get("threading", True)
            self.sleep_time = bot.get("sleep_time", 0.4)


def get_config(config: Config = Config()) -> Config:
    return config