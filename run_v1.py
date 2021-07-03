from genericpath import exists
from pprint import pprint
from movies import *
from models import ShowWrapper, NewsWrapper
from db_models import *
from requests_html import HTMLSession
from tabulate import tabulate
import sys
import os
import re
import json
import datetime
from sqlalchemy import desc

import urllib3

urllib3.disable_warnings()

parent_dir = os.path.abspath(os.path.join(__file__, ".."))


class MeijumiManager():

    news_json_file = os.path.join(parent_dir, 'news.json')
    shows_data_dir = os.path.join(parent_dir, 'shows_data')
    db_file = os.path.join(parent_dir, "data.db")

    def __init__(self, db_session=None) -> None:
        """
        date: [{ show: str, url: str, episode: str, date: str }]
        """
        self.s = HTMLSession()
        # self.engine = sqlalchemy.create_engine(db_uri)
        self.news_data = []
        self.shows = []
        self.shows_data = {}
        self.db_session = db_session
        if not os.path.exists(self.news_json_file):
            print("{} not existe. Create one".format(self.news_json_file))
            with open(self.news_json_file, 'a') as f:
                f.write('[]')
        if not os.path.exists(self.shows_data_dir):
            print("{} not existe. Create one".format(self.shows_data_dir))
            os.system('mkdir ' + self.shows_data_dir)

    def initialize(self):
        self.load_json()
        self.load_db()
        print("Synchronizing show database with news json file...")
        self.synchronize_shows()

    def load_json(self):
        with open(self.news_json_file) as f:
            self.news_data = json.load(f)
        for f in os.listdir(self.shows_data_dir):
            if f[-5:] == '.json':
                self.shows_data[f[:-5]] = self.load_one_show_json(f[:-5])
        print("{} shows data loaded".format(len(self.shows_data)))

    def update_database_from_news_data(self):
        print("Updating database from json file...")
        for line in self.news_data:
            line['date'] = datetime.datetime.strptime(
                line['date'], "%Y-%m-%d").date()
            show = self.db_session.query(Show).filter(
                Show.meijumi_url == line['url'])
            if show == []:
                print("No show named {} found".format(line['show']))
                continue
            else:
                show = show.one()

                # update operations
                show.last_update = line['date']
                print("Update last_update {} for show {}".format(
                    line['date'], line['show']))

                # self.shows.append(show)
        print("Commiting changes...")
        self.db_session.commit()
        print("Done")

    # database related methods

    def load_db(self):
        self.shows = [ShowWrapper(show) for show in self.db_session.query(
            Show).order_by(desc(Show.last_update)).all()]
        print("{} shows loaded from the database".format(len((self.shows))))

    def synchronize_shows(self, news=None):
        news = news if news else self.news_data
        new_shows = []
        updated_shows = []
        for line in news:
            show_id = extract_meijumi_id(line['url'])
            show = self.db_session.query(Show).filter(
                Show.meijumi_id == show_id).all()
            if show == []:
                print("No show named {} found. Creating one".format(
                    line['show']))
                show = Show(name=line['show'], meijumi_id=show_id)
                new_shows.append(show)
                continue
            else:
                show = show[0]
                new_date = datetime.datetime.strptime(
                    line['date'], '%Y-%m-%d').date()
                if show.last_update is None or show.last_update < new_date:
                    show.last_update = new_date
                    updated_shows.append(show)
                if show not in self.shows:
                    self.shows.append(show)
        if len(new_shows) != 0 or len(updated_shows) != 0:
            if len(new_shows) != 0:
                self.db_session.add_all(new_shows)
                self.shows += new_shows
            self.db_session.commit()
        print("{} shows updated.".format(len(updated_shows)))
        print("{} new show(s) created.".format(len(new_shows)))

    def save_new_shows(self):
        for show in self.shows:
            self.db_session.append(show)
        self.db_session.commit()
        print("Saved {} shows to the database".format(len(self.shows)))

    def get_update(self):
        """
        Get show update using Meijumi API (/news), then save the new show to the database.
        """
        results = get_news100(self.s)

        if self.news_data != []:
            latest = self.news_data[0]
            new_episodes = []
            for e in results:
                if e['show'] == latest['show'] and e['episode'] == latest['episode']:
                    break
                new_episodes.append(e)
            self.news_data = new_episodes + self.news_data
            print("{} new episodes retrieved".format(len(new_episodes)))
            self.synchronize_shows(news=new_episodes)
            self.get_shows(show_id_list=map(
                lambda x: extract_meijumi_id(x['url']), new_episodes))
        else:
            print("No record stored")
            self.news_data = results

        with open(self.news_json_file, 'w') as f:
            json.dump(self.news_data, f)
        print("{} episode record saved".format(len(self.news_data)))

        # self.synchronize_shows()
        # self.save_shows()

    # show related methods

    def pprint_shows(self, shows=None, i: int = 10):
        shows = shows if shows else self.shows
        temp_shows = map(lambda x: (x.name, str(x.last_update),
                         x.url), shows[:i])
        print(tabulate(temp_shows))

    def pprint_show_episode_output(self, output):
        def print_block(block):
            # print("Start block")
            print()
            block_output = []
            for line in block:
                # print("Start line")
                # print(str(line))
                line_temp = []
                for item in line:
                    # print("Start item")
                    # print(str(item[1]))
                    if item[0] is not None:
                        passcode = ''
                        if len(item) >= 3 and item[2] != '':
                            passcode = '(' + item[2] + ')'
                        temp_item = '\x1b[94m{}{}\x1b[37m'.format(
                            item[1], passcode)
                    else:
                        temp_item = '\x1b[37m' + item[1]
                    line_temp.append(temp_item)
                    print(temp_item, end='  ')
                block_output.append(line_temp)
                print()
        for block in output:
            print_block(block)

    def save_one_show_json(self, show_id, data):
        filepath = os.path.join(self.shows_data_dir, show_id + '.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        print("Save {}".format(filepath))

    def load_one_show_json(self, show_id):
        filepath = os.path.join(self.shows_data_dir, show_id + '.json')
        if not os.path.exists(filepath):
            print('{} do not exist!'.format(filepath))
            return
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)

    def get_shows(self, show_id_list=None):
        show_id_list = show_id_list if show_id_list else map(
            lambda x: x.meijumi_id, self.shows)
        for show_id in show_id_list:
            self.get_show(show_id=show_id)

    def get_show(self, show_id=None, url=None):
        """
         - recieve a Model object, 
         - extract the show url from show.meijumi_id, 
         - send and get the html of the show page
         - parse the page to get show information
         - parse the page to get episode information

        Parameters: must provide either a Show object or an url

        Return value: (show_info, episode_info)
        """
        if show_id is None and url is None:
            print("No show_id or url is provided")
            return
        url = construct_meijumi_show_url(show_id) if show_id else url
        show_id = extract_meijumi_id(url) if not show_id else show_id
        print("Trying to get show url " + url)
        res = self.s.get(url, verify=False)
        show_info = self.extract_show_info(res)
        episode_info = self.extract_episodes(res)
        show_data = {
            'show_info': show_info,
            'episode_info': episode_info
        }
        self.save_one_show_json(show_id, show_data)
        return show_data

    def extract_show_info(self, res):
        content = res.html.find('.single-content')[0].html
        # title = re.findall(
        #     u'《(.+?)》', res.html.find('h1.entry-title')[0].html)[0]
        title = re.findall(
            u'《(.+?(?:第(?:.+?)季)?)》', res.html.find('h1.entry-title')[0].html
        )[0]

        try:
            original_name = re.findall(
                u'英文全名(.+?)(?:\s*?\(\d{4}\))', content
                # u'英文全名(.+?)(?:\sSeason\s\d{1,2})?(?:\s\s\(\d{4}\))', content
            )
            if original_name == []:
                raise Exception("Parsing Error")
            original_name = original_name[0]
        except Exception as e:
            print("Error parsing original name")
        img = re.findall(u'<img.+?src="(.+?)".+?>', content)[0]
        # season = re.findall(u'第(\w)季', title)[0]
        return {
            'name': title,
            'original_name': original_name,
            'img': img,
            # 'season': season
        }

    def extract_episodes(self, res):
        """
        Extract episode information from a response of a show page
        Return format: [
            [ # a block
                [ # a line/episode
                    {
                        name: str
                        url: str | None
                        passcode: str | None
                    }
                ]
            ]
        ]
        """
        p_list = res.html.find('.single-content')[0].find('p')
        output = []
        for p in p_list:
            p = p.html
            # if 'FIX字幕侠高清资源' in p:
            #     lines = re.findall(u'((?:<a.+?>)?S\d{2}E\d{2}.+?(?:</p>|<br>|<br/>))', p)
            temp_1 = []
            lines = re.findall(
                u'((?:<a.+?>)?S\d{2}E\d{2}.+?(?:</p>|<br>|<br/>))', p)
            if lines == []:
                continue
            for line in lines:
                items_1 = re.split(u'\s\|\s', line)
                items_2 = re.split(u'\s\s', line)
                if len(items_1) == 1 and len(items_2) != 1:
                    items = items_2
                else:
                    items = items_1
                temp_items = []
                for i, item in enumerate(items):

                    temp = re.findall(
                        u'<a href="(.+?)"[^>]+?>(.+?)</a>(?:\s(.{4}))?', item)
                    # (url, name, passcode)

                    if not temp:
                        temp_item = item.replace('<br>', '').replace(
                            '<br/>', '').replace('</p>', '')
                        temp_item = [None, temp_item, None]
                    else:
                        temp_item = list(temp[0])

                    if i == 0:
                        e_name = re.findall(u'S\d{2}E\d{2}', line)[0]
                        if temp_item[1][:6] != e_name:
                            temp_item[1] = e_name + '.' + temp_item[1]
                    temp_items.append(temp_item)
                temp_1.append(temp_items)
            output.append(temp_1)
        return output

    def latest_episode(self, episode_info):
        latest = None
        i = 0
        for block in episode_info:
            for e in block[::-1]:
                has_link = False
                for item in e:
                    has_link = has_link or item[0] is not None
                if has_link:
                    latest = e
                    break

    def latest_episodes(self):
        for show in self.shows:
            show_data = self.shows_data[show.meijumi_id]

    def pprint_latest(self, i: int = 10):
        output = map(lambda x: (x.name, x.last_update,
                     x.url), self.shows[:i])
        print(tabulate(output))
        # self.pprint_show_episode_output(
        #     self.shows_data[show_id]['episode_info'])


def loop_shows(manager: MeijumiManager):
    # temp_shows = []
    for i, show in enumerate(manager.shows[:2]):
        url = show.url
        print(i)
        output = manager.get_show(url=url)
        show_info = output['show_info']
        episode_info = output['episode_info']

        pprint(show_info)
        # manager.save_one_show_json(show.meijumi_id, output)

    #     print(show.name)

    #     # show.original_name = show_info['original_name']
    #     show.img = show_info['img']
    #     show.name = show_info['name']
    #     manager.db_session.commit()

        # temp = []
        # episodes = []
        # for block in episode_info:
        #     for e in block:
        #         episode_obj = Episode(show=show)
        #         temp_single_e = []
        #         links = []
        #         for i,i_info in enumerate(e):
        #             link = Link(episode=episode_obj)
        #             link.url = i_info[0]
        #             link.name = i_info[1]
        #             link.passcode = i_info[2]
        #             if i == 0:
        #                 episode_obj.name = i_info[1]
        #             temp_single_e.append(i_info)
        #             links.append(link)
        #         temp.append(temp_single_e)
        #         episodes.append((episode_obj, links))
        #         manager.db_session.add(episode_obj)
        #         manager.db_session.add_all(links)
        # pprint(temp)
        # pprint(episodes)

        print()


def main():
    manager = MeijumiManager(db_session=session)
    manager.initialize()
    # manager.load_db()
    # pprint(manager.news_data)
    # pprint(manager.shows)

    # change all url to id
    # for show in manager.shows:
    #     url = show.meijumi_id
    #     _id = extract_meijumi_id(url)
    #     show.meijumi_id = _id
    # manager.db_session.commit()

    # loop_shows(manager)

    if len(sys.argv) > 1 and sys.argv[1] == 'url':
        url = sys.argv[2]
        print(url)
        show_data = manager.get_show(url=url)
        manager.pprint_show_episode_output(show_data['episode_info'])
    elif len(sys.argv) > 1 and sys.argv[1] == 'shows':
        if len(sys.argv) > 2:
            manager.pprint_latest(i=int(sys.argv[2]))
        else:
            # pprint(manager.shows)
            # manager.pprint_shows()
            manager.pprint_latest()
    elif len(sys.argv) > 1 and sys.argv[1] == 'update':
        manager.get_update()
        manager.pprint_latest()
    elif len(sys.argv) > 1 and sys.argv[1] == 'news':
        print(tabulate(manager.news_data))


if __name__ == '__main__':
    main()
