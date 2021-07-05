import json
from models import ShowList, EpisodeNewsList


class SubscribedDataManager(object):
    """
    This class manages a subscriber's data, including shows and episode news.

    A user can 
     - add, or delete show(s) from his/her subscribed show list;
     - print out their subscribed shows;
     - print out the episode news of their subscribed shows;
    """

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

    def add_show(self, show_obj, save=True):
        """
        Add a new show to the subscribed shows, given the show id.
        """
        if show_obj not in self.shows:
            self.shows.append_one(show_obj)
            if save:
                self.save()
            # print("Add show {} to the subscribed show list".format(show_obj))
        else:
            # print(
            # "Show with ID {} is already in the subscribed shows!".format(show_obj.meijumi_id))
            return False

    def add_show_by_id(self, show_id, save=True):
        """
        Add a new show to the subscribed shows, given the show id.
        """
        show_obj = self._shows_source.find_by_id(show_id)
        if show_obj:
            return self.add_show(show_obj, save=save)
        else:
            return False

    def delete_show(self, show_obj, save=True):
        if show_obj in self.shows:
            self.shows.delete_one(show_obj)
            if save:
                self.save()
            print("Delete show {} from the subscribed show list".format(show_obj))
            return True
        else:
            return False

    def delete_show_by_id(self, show_id, save=True):
        """
        Delete a show from the subscribed list, given the show id.
        """
        show_obj = self.shows.find_by_id(show_id)
        if show_obj:
            self.delete_show(show_obj)
        else:
            return False
