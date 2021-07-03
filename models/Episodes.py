from .base import ObjectModelBase
from .Show import Show


class Episodes(ObjectModelBase):
    def __init__(self, show: Show = None, blocks: list = []) -> None:
        super().__init__()
        self.show = show
        self.blocks = blocks
