from .base import ObjectModelBase
from .Show import Show


class EpisodeNews(ObjectModelBase):
    def __init__(self, show='', url='', episode='', date='', **kwargs) -> None:
        super().__init__(episode=episode, **kwargs)
        self.show: Show = Show()
        self.show.name = show
        self.show.url = url
        self.show.last_update = date

    @property
    def name(self):
        return self.show.name

    @name.setter
    def name(self, value):
        self.show.name = value

    @property
    def name(self):
        return self.show.name

    @name.setter
    def name(self, value):
        self.show.name = value

    @property
    def url(self):
        return self.show.url

    @url.setter
    def url(self, value):
        self.show.url = value

    @property
    def episode(self):
        return self.data['episode']

    @episode.setter
    def episode(self, value):
        self.data['episode'] = value

    @property
    def date(self):
        return self.show.last_update

    @date.setter
    def date(self, value):
        self.show.last_update = value

    def __str__(self) -> str:
        return "{}\t{}\t{}".format(self.show.name, self.episode, self.date)

    def __repr__(self) -> str:
        return '<EpisodeNews show="{}" url="{}" episode="{}" date="{}">'.format(
            self.name, self.url, self.episode, self.date)

    def json(self) -> str:
        return {
            'show': self.show.name,
            'url': self.show.url,
            'episode': self.episode,
            'date': str(self.show.last_update)
        }

    def array(self) -> tuple:
        return (self.date, self.name, self.episode, self.url)

    def __hash__(self) -> int:
        return hash((self.show.meijumi_id, self.episode, self.date))

    def __eq__(self, o: object) -> bool:
        return self.show == o.show and self.episode == o.episode and self.date == o.date

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    # def __gt__(self, o: object) -> bool:
    #     return self.show == o.show and self.episode == o.episode and self.date > o.date

    # def __lt__(self, o: object) -> bool:
    #     return self.show == o.show and self.episode == o.episode and self.date < o.date

    # def __ge__(self, o: object) -> bool:
    #     return self.show == o.show and self.episode == o.episode and self.date >= o.date

    # def __le__(self, o: object) -> bool:
    #     return self.show == o.show and self.episode == o.episode and self.date <= o.date
