from models import *
import os
import sys
import json

import urllib3
urllib3.disable_warnings()

parent_dir = os.path.abspath(os.path.join(__file__, ".."))


class SubscribedShowManager(object):
    def __init__(self, shows_source: ShowList = None, news_source: EpisodeNewsList = None, json_path: str = '') -> None:
        self.json_path: str = json_path
        self._shows_source: ShowList = shows_source
        self._news_source: EpisodeNewsList = news_source
        self._show_id_list = []
        self.shows: ShowList = ShowList()
        self.news: EpisodeNewsList = EpisodeNewsList()
        self.load_json()

    def load_json(self):
        if self.json_path:
            with open(self.json_path) as f:
                self._show_id_list = json.load(f)

            # load the show objects from show id list
            self.load_shows()

            # load the episode news of the subscribed shows
            self.load_news()

            print("Finish loading {} subscribed show(s)...".format(
                len(self.shows)))

    def load_shows(self):
        """
        Load a list of Show objects from self._show_id_list, stored in self.shows.
        """
        for show_id in self._show_id_list:
            self.add_show_by_id(show_id, save=False)

    def load_news(self):
        """
        Load a list of Show objects from self._show_id_list, stored in self.news.
        """
        self.news.data = list(
            filter(lambda n: n.show in self.shows, self._news_source))

    def save(self):
        show_id_list = [s.meijumi_id for s in self.shows]
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(show_id_list, f)
        print("{} subscribed shows ID saved".format(len(show_id_list)))

    def add_show_by_id(self, show_id, save=True):
        """
        Add a new show to the subscribed shows, given the show id.
        """
        show_obj = self._shows_source.find_by_id(show_id)
        if show_obj:
            self.shows.append_one(show_obj)
            if save:
                self.save()
            print("Add show {} to the subscribed show list".format(show_obj))
        else:
            print(
                "Show with ID {} not found in show database!".format(show_id))
            return False

    def delete_show_by_id(self, show_id, save=True):
        """
        Delete a show from the subscribed list, given the show id.
        """
        show_obj = self.shows.find_by_id(show_id)
        if show_obj:
            self.shows.delete_one(show_obj)
            if save:
                self.save()
            print("Delete show {} from the subscribed show list".format(show_obj))
            return True
        else:
            return False


class MeijumiDataManager(object):

    PATHS = {
        "shows": os.path.join(parent_dir, 'data', 'shows.json'),
        "episodes": os.path.join(parent_dir, 'data', 'episodes.json'),
        "news": os.path.join(parent_dir, 'data', 'news.json'),
    }

    def __init__(self) -> None:
        """
        Initialize the manager: check if paths of each json file, then load them.
        """
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


def main():
    data_manager = MeijumiDataManager()
    data_manager.synchronize_shows_from_news()

    subscribed_path = os.path.join(parent_dir, 'data', 'subscribed.json')
    subscribed_manager = SubscribedShowManager(
        shows_source=data_manager.shows,
        news_source=data_manager.news,
        json_path=subscribed_path)

    # url = "https://www.meijumi.net/usa/mohuan/"
    # new_shows = manager.shows.extract_links_from_url(url)
    # print(manager.shows.unique())
    # print(new_shows[0].json())
    # print(len(new_shows))
    # manager.shows.get_all(shows=new_shows)

    if len(sys.argv) == 1:
        print("\nCurrent subscribed shows:")
        subscribed_manager.shows.pretty_print()
        print("\nCurrent episode news of subscribed shows:")
        subscribed_manager.news.pretty_print()
    elif sys.argv[1] == 'update':
        data_manager.news.update()
        data_manager.synchronize_shows_from_news()
    elif sys.argv[1] == 'show':
        if len(sys.argv) == 3:
            show_id = sys.argv[2]
            show = data_manager.shows.find_by_id(show_id)
            if show:
                print("\nShow information of {}:".format(show_id))
                print(show.pretty())
            else:
                print("\nShow with ID {} not found".format(show_id))
    elif sys.argv[1] == 'shows':
        if len(sys.argv) == 3:
            count = int(sys.argv[2])
        else:
            count = 10
        data_manager.shows.print_latest(count=count)

    elif sys.argv[1] == 'news':
        if len(sys.argv) == 3:
            count = int(sys.argv[2])
        else:
            count = 10
        print('\n{} latest episode news:'.format(count))
        data_manager.news.pretty_print(count=count)

    elif sys.argv[1] == 'subscribed':
        if len(sys.argv) == 4 and sys.argv[2] == 'add':
            show_id = sys.argv[3]
            subscribed_manager.add_show_by_id(show_id)
        elif len(sys.argv) == 4 and sys.argv[2] == 'delete':
            show_id = sys.argv[3]
            subscribed_manager.delete_show_by_id(show_id)
        else:
            subscribed_manager.news.pretty_print()
        print("\nCurrent subscribed shows:")
        subscribed_manager.shows.pretty_print()

    # show_info, e_info = manager.update_show(manager.shows[0].url)
    # print(show_info)
    # manager.save_shows()

    # manager.synchronize_shows_from_news()

    # shows_without_img = list(
    #     filter(lambda s: not s.last_update, manager.shows))
    # print(len(shows_without_img))

    # for show in manager.shows[:5]:
    #     show.get_show()
    # print(show.json())
    # manager.update_show(show.url)
    # sleep(1)
    # manager.save_shows()

    # for n in manager.news:
    # print(n.show.meijumi_id, n.show)
    # print(type(n.show))


if __name__ == '__main__':
    main()
