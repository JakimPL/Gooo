import json


class Config:
    def __init__(self):
        with open("config.json") as file:
            _data = json.load(file)
            _model = _data['model']
            self.alpha = _model['alpha']
            self.max_len = _model['max_len']
            self.batch_size = _model['batch_size']
            self.power = 1 - _model['randomness']
            self.gamma = _model['gamma']
            self.layers = _model['layers']

            _game = _data['game']
            self.x_offset = _game['x_offset']
            self.y_offset = _game['y_offset']
            self.tile_size = _game['tile_size']
            self.rim_size = _game['rim_size']
            self.panel_width = _game['panel_width']
            self.font = _game['font']
