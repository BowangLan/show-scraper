from .models import *


def main():
    name = 'Shit Show'
    show_id = '12333'
    url = 'https://www.meijumi.net/12345.html'
    date = '2021-08-31'

    show = Show(name=name,
                url=url, last_update=date)
    print(show.json())

    show = Show(name=name, meijumi_id=show_id, last_update=date)
    print(show.json())
    print(show.url)

    e = EpisodeNews(name=name, url=url, episode='S01E03', date=date)
    print(e.json())
    print(e.show.json())
    e2 = EpisodeNews(name=name, url=url, episode='S01E03', date=date)
    print(e == e2)


if __name__ == '__main__':
    main()
