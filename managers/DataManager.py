import json
import os
from models import ShowList, EpisodeNewsList, EpisodesList


class MeijumiDataManager(object):

    def __init__(self, parent_dir: str) -> None:
        """
        Initialize the manager: check if paths of each json file, then load them.
        """
        self.PATHS = {
            "shows": os.path.join(parent_dir, 'data', 'shows.json'),
            "episodes": os.path.join(parent_dir, 'data', 'episodes.json'),
            "news": os.path.join(parent_dir, 'data', 'news.json'),
        }
        self.check_path()
        self.shows = ShowList(json_path=self.PATHS['shows'])
        self.episodes = EpisodesList(json_path=self.PATHS['episodes'])
        self.news = EpisodeNewsList(json_path=self.PATHS['news'])
        # self.subscribed = SubscribedShowManager(
        #     shows_source=self.shows,
        #     news_source=self.news,
        #     json_path=self.PATHS['subscribed'])

    """
    ###################################
    Methods for loading and saving data
    ###################################
    """

    def check_path(self):
        """
        Check if the json file paths exist.
          If not, create the file with [] as content.
        """
        for path in self.PATHS.values():
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump([], f)

    """
    ######################################
    Methods for maintaining data integraty
    ######################################
    """

    def update_shows_from_news(self, news=None, save=True):
        """
        Find and save new shows from the news data.
        :param news: list of news from which to update.
        """
        print("Updating shows from news...")
        news = news if news else self.news.data
        potential_new_shows = self.news.unique_shows(news=news)
        new_shows = self.shows.append_many(potential_new_shows)
        if save:
            self.shows.save()
        print("{} new show(s) found and saved".format(len(new_shows)))

    def synchronize_shows_from_news(self, news=None):
        print("\nSynchronizing shows from episode news...")
        news = news if news else self.news.data
        self.update_shows_from_news(news=news, save=False)
        update_count = 0
        for n in news:
            show = list(filter(lambda s: s == n.show, self.shows))[0]
            if show.last_update:
                if n.date > show.last_update:
                    show.last_update = n.date
                    update_count += 1
            else:
                show.last_update = n.date
        self.shows.save()
        print("{} shows updated and saved".format(update_count))
