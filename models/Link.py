from .base import ObjectModelBase


class Link(ObjectModelBase):
    def __str__(self) -> str:
        return self.data['name']

    def __repr__(self) -> str:
        return '<Link name="{}" >'.format(self.data['name'])

    def json(self):
        return {
            'url': self.data['url'],
            'name': self.data['name'],
            'passcode': self.data['passcode']
        }
