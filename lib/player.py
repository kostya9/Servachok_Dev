from typing import List


class Player(object):
    def __init__(self, address: tuple, player_id: int):
        self.address = address
        self.id = player_id
        self.ready = False
        self.rendered = False
        self.object_ids: List[int] = []
        self.name = 'client {}'.format(self.id)

    def info(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'ready': self.ready,
        }
