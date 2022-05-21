import json


class Config:
    def __init__(self):
        with open("config.json") as file:
            data = json.load(file)
            ui = data["ui"]
            self.x_offset = ui.get("x_offset", 16)
            self.y_offset = ui.get("y_offset", 16)
            self.tile_size = ui.get("tile_size", 64)
            self.rim_size = ui.get("rim_size", 2)
            self.panel_width = ui.get("panel_width", 600)
            self.font = ui.get("font", "Noto Mono")

            bot = data["bot"]
            self.threading = bot.get("threading", True)
            self.sleep_time = bot.get("sleep_time", 0.4)


def get_config(config: Config = Config()) -> Config:
    return config