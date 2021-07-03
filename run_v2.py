from time import sleep
from web import *
import os
import json
from tabulate import tabulate

parent_dir = os.path.abspath(os.path.join(__file__, ".."))


class MeijumiManager(object):

    SHOWS_PATH = os.path.join(parent_dir, 'shows.json')
    EPISODES_PATH = os.path.join(parent_dir, 'episodes.json')
    NEWS_PATH = os.path.join(parent_dir, 'news.json')

    def __init__(self) -> None:
        """
        Initialize the manager with empty data. 
        """
        self.shows = []
        self.episodes = []
        self.news = []
        self.api = MeijumiAPI()

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
        for path in [self.SHOWS_PATH, self.EPISODES_PATH, self.NEWS_PATH]:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump([], f)

    def load_data(self):
        """
        Load all three kinds of data(shows, news, episodes)
         from the respective json files.
        """
        self.load_shows()
        self.load_episodes()
        self.load_news()

    def load_json(self, path):
        """
        Utility method for loading json file.
        """
        with open(path) as f:
            return json.load(f)

    def save_json(self, data, path):
        """
        Utility method for saving data to json file.
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_shows(self):
        """
        Load shows data from json file, and 
        convert each item into a Show object.
        File path is specified in self.SHOWS_PATH
        """
        shows = self.load_json(self.SHOWS_PATH)
        for show in shows:
            self.shows.append(Show(**show))
        print("{} shows loaded from json file".format(len(self.shows)))

    def save_shows(self):
        """
        Convert each show item into json by calling Show.json();
          save the converted shows data into the specified json file.
        """
        self.shows = sorted(
            self.shows, key=lambda s: s.meijumi_id, reverse=True)
        data = [i.json() for i in self.shows]
        self.save_json(data, self.SHOWS_PATH)
        print("{} shows saved into json file".format(len(data)))

    def load_episodes(self):
        """
        Load episodes data from json file. 
        File path is specified in self.EPISODES_PATH
        """
        self.episodes = self.load_json(self.EPISODES_PATH)
        print("{} episodes loaded from json file".format(len(self.episodes)))

    def save_episodes(self):
        """
        Save the episodes data into the specified json file.
        """
        data = [i.json() for i in self.episodes]
        self.save_json(data, self.EPISODES_PATH)
        print("{} episodes saved into json file".format(len(self.episodes)))

    def load_news(self):
        """
        Load episode news data from json file, and 
          convert each item to an EpisodeNews object.
        File path is specified in self.NEWS_PATH
        """
        news = self.load_json(self.NEWS_PATH)
        for n in news:
            self.news.append(EpisodeNews(**n))
        print("{} episode news loaded from json file".format(len(self.news)))

    def save_news(self):
        """
        Sort the episode news according to date descendingly;
          convert each news item into json with EpisodeNews.json() method;
          save the converted news data into the specified json file.
        """
        self.news = sorted(self.news, key=lambda x: x.date, reverse=True)
        data = [i.json() for i in self.news]
        self.save_json(data, self.NEWS_PATH)
        print("{} episode news saved into json file".format(len(data)))

    """
    ######################################
    Methods for updating data from the API
    ######################################
    """

    def update_news(self):
        """
        Update the episode news data using MeijumiAPI.get_news() method; 
          insert the new episodes into the front of the existing episode news data;
          print out the new episodes;
          save the updated episode news data;
          parse and save the new shows from the episode news.
        Return value: number of new episodes retrieved.
        """
        output = self.api.get_news()
        latest = self.news[0]
        new_episodes = []
        for s in output:
            if s.date == latest.date and s.show == latest.show:
                break
            else:
                new_episodes.append(s)
        self.news = new_episodes + self.news

        # save the updated episode news
        self.save_news()
        print("{} new episode(s) retrieved and saved".format(len(new_episodes)))

        if new_episodes:
            # print out the new episodes if there is any
            self.print_news(i=len(new_episodes))

            # parse and save the new shows
            self.update_shows_from_news(news=new_episodes)

        return len(new_episodes)

    def update_show(self, url):
        """
        Update show information using MeijumiAPI.get_show(url);
        """
        old_show = list(filter(lambda s: s.url == url, self.shows))

        if not old_show:
            old_show = None
        else:
            old_show = old_show[0]

        show, episode_info = self.api.get_show(url)

        if old_show:
            old_show.merge(show)
        else:
            old_show = show
            self.shows.append(old_show)

        print("Show updated: {}\t{}".format(
            old_show.meijumi_id, old_show.name))
        # print(old_show.json())
        return old_show, episode_info

    """
    ################################
    Methods for pretty printing data
    ################################
    """

    def print_news(self, i=10):
        """
        Pretty print news data, start the the latest.
        :param i: number of news printed
        """
        data = [(n.name, n.date, n.episode, n.url)
                for n in self.news[:i]]
        print(tabulate(data, tablefmt='plain'))

    def pprint_show_episode_output(self, output):
        """
        Pretty print the output of episode information of a show.
        """
        def print_block(block):
            print()
            block_output = []
            for line in block:
                line_temp = []
                for item in line:
                    if item['url']:
                        temp_item = '\x1b[94m{}{}\x1b[37m'.format(
                            item['name'], item['passcode'])
                    else:
                        temp_item = '\x1b[37m' + item['name']
                    line_temp.append(temp_item)
                    print(temp_item, end='  ')
                block_output.append(line_temp)
                print()
        for block in output:
            print_block(block)

    """
    ######################################
    Methods for maintaining data integraty
    ######################################
    """

    def news_unique(self):
        news_length = len(self.news)
        set_news_length = len(set(self.news))
        return news_length == set_news_length

    def shows_unique(self):
        news_length = len(self.shows)
        set_news_length = len(set(self.shows))
        return news_length == set_news_length

    def update_shows_from_news(self, news=None, save=True):
        """
        Find and save new shows from the news data.
        :param shows: list of news from which to update.
        """
        news = news if news else self.shows
        new_shows = []
        for n in self.news:
            if n.show not in self.shows and n.show not in new_shows:
                new_shows.append(n.show)
        self.shows += new_shows
        if save:
            self.save_shows()
        print("{} new show(s) found and saved".format(len(new_shows)))

    def synchronize_shows_from_news(self, news=None):
        news = news if news else self.shows
        self.update_shows_from_news(news=news, save=False)
        update_count = 0
        for n in self.news:
            show = list(filter(lambda s: s == n.show, self.shows))[0]
            if show.last_update:
                if n.date > show.last_update:
                    show.last_update = n.date
                    update_count += 1
            else:
                show.last_update = n.date
        self.save_shows()
        print("{} shows updated last_update and saved".format(update_count))


def main():
    manager = MeijumiManager()
    manager.check_path()
    manager.load_data()
    # print(manager.shows[1].json())
    # print(manager.news[0].json())

    # i = manager.update_news()
    # manager.get_news(i=30)

    # show_info, e_info = manager.update_show(manager.shows[0].url)
    # print(show_info)
    # manager.save_shows()

    # manager.synchronize_shows_from_news()

    # shows_without_img = list(
    #     filter(lambda s: not s.last_update, manager.shows))
    # print(len(shows_without_img))

    for show in manager.shows[:5]:
        show.get_show()
        # print(show.json())
        # manager.update_show(show.url)
        # sleep(1)
    # manager.save_shows()

    # for n in manager.news:
    # print(n.show.meijumi_id, n.show)
    # print(type(n.show))


if __name__ == '__main__':
    main()
