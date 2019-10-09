from typing import List


class Player(object):
    def __init__(self, address: tuple, id_: int):
        self.address = address
        self.id = id_
        self.ready = False
        self.rendered = False
        self.object_ids: List[int] = []
        self.name = 'client {}'.format(self.id)

    def get_sender_event_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'ready': self.ready,
        }

    def is_ready(self) -> bool:
        return self.ready

    def is_rendered(self) -> bool:
        return self.rendered
