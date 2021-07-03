from time import perf_counter
from requests_html import HTMLSession
from tabulate import tabulate
from .base import ObjectListBase
from .EpisodeNews import EpisodeNews


class EpisodeNewsList(ObjectListBase):
    def __init__(self, **kwargs) -> None:
        kwargs['child_class'] = EpisodeNews
        super().__init__(**kwargs)

    def save(self):
        self.data = sorted(self.data, key=lambda x: x.date, reverse=True)
        super().save()

    # def pretty(self, i=10):
    #     """
    #     Pretty print episode news data, start the the latest.
    #     :param i: number of news printed
    #     """
    #     data = [n.array() for n in self.data[:i]]
    #     return tabulate(data, tablefmt='plain')

    def update(self):
        """
        Retrieve, merge, and save new episode information.
        Return True if there are new episodes appended, else return False.
        """
        NEWS_API = 'https://www.meijumi.net/news/'
        print("\nUpdating episode news...")

        # send the request
        with HTMLSession() as s:
            tic = perf_counter()
            res = s.get(NEWS_API, verify=False, proxies=None)
            print(f"Get page in {perf_counter() - tic:0.4f} seconds")

        # parse the response
        output = []
        result = res.html.find('.news100')
        for i, line in enumerate(result):
            spans = line.find('span')
            episode_news = EpisodeNews(
                show=spans[0].text,
                url=spans[0].find('a')[0].attrs['href'],
                episode=spans[1].text,
                date=spans[3].text
            )
            # 'category': spans[2].text,
            output.append(episode_news)

        # marge with existing episode news
        latest = self.data[0]
        new_episodes = []
        for s in output:
            if s.date == latest.date and s.show == latest.show:
                break
            else:
                new_episodes.append(s)
        self.data = new_episodes + self.data

        # save the updated episode news
        self.save()
        print("{} new episode(s) retrieved and saved".format(len(new_episodes)))

        # if len(new_episodes) != 0:
        #     print(self.pretty())

        return len(new_episodes) == 0

    def unique_shows(self, news=None):
        """
        Return all unique shows in the episode news data.
        """
        news = news if news else self.data
        shows = list(set([n.show for n in news]))
        return shows
