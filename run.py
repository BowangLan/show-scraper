import desktop_notify
import time
from models import *
from managers import *
from queries import *
import os
import sys

import urllib3
urllib3.disable_warnings()


parent_dir = os.path.abspath(os.path.join(__file__, '..'))


def clear_screen():
    print('\x1b[3J\x1b[H')


def run(data_manager, subscribed_manager):
    delay = 300
    print("Start running...")
    # server = desktop_notify.Server()
    while True:
        new_episode_length = data_manager.news.update()
        if new_episode_length:
            data_manager.news.pretty_print(count=new_episode_length)
            # n = server.Notify()
            msg = '{} new episode retrieved!'.format(new_episode_length)
            # n = desktop_notify.aio.Notify(msg, time.ctime())
            # await n.show()
        clear_screen()
        print('Last update:', time.ctime())
        data_manager.news.pretty_print(count=10)
        time.sleep(delay)


def main():
    data_manager = MeijumiDataManager(parent_dir)
    data_manager.synchronize_shows_from_news()

    subscribed_path = os.path.join(parent_dir, 'data', 'subscribed.json')
    subscribed_manager = SubscribedDataManager(
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

    elif len(sys.argv) == 2 and sys.argv[1] == 'run':
        run(data_manager, subscribed_manager)
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

    elif len(sys.argv) >= 3 and sys.argv[1] == 'search':
        if len(sys.argv) >= 4:
            count = int(sys.argv[3])
        else:
            count = 10
        keyword = sys.argv[2]
        # data = data_manager.shows.filter(
        #     lambda item: item.name and keyword in item.name,
        #     inplace=False)
        data = list(search_show_name(data_manager.shows, keyword))
        print("\n{} search result(s) found for \"{}\":".format(
            len(data), keyword))
        data_manager.shows.pretty_print(data=data, count=count)

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
