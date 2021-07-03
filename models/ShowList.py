import re
from requests_html import HTMLSession
from tabulate import tabulate
from .base import ObjectListBase
from .Show import Show


class ShowList(ObjectListBase):
    def __init__(self, **kwargs) -> None:
        kwargs['child_class'] = Show
        super().__init__(**kwargs)

    def save(self):
        self.sort(key=lambda item: item.meijumi_id)
        super().save()

    def update_all(self, shows=[], save=True):
        """
        Update information of the given list of shows.
        If no show list is given, update all.
        """
        shows = shows if shows else self.data
        for show in shows:
            show.get_show()
        if save:
            self.save()

    def extract_links_from_url(self, url):
        """
        Extract all unique show url(s) from a page, given the url.
        Return a list of founded show id.
        """
        with HTMLSession() as s:
            res = s.get(url, verify=False)

        id_list = re.findall(
            u'https://www.meijumi.net/(\d+)\.html', res.html.html)
        id_list = list(set(id_list))  # remove duplicates
        print("{} unique show id found".format(len(id_list)))
        shows_extracted = [Show(meijumi_id=_id) for _id in id_list]
        shows_added = self.append_many(shows_extracted)
        return shows_added

    def find_by_id(self, show_id):
        """
        Return the show with given show id.
        """
        result = list(filter(lambda s: s.meijumi_id == show_id, self.data))
        if result:
            return result[0]
        else:
            return None

    def sort_by_id(self, **kwargs):
        """
        Sort shows by their id.
        """
        kwargs['key'] = lambda s: s.meijumi_id
        return super().sort(**kwargs)

    def sort_by_date(self, **kwargs):
        """
        Sort shows by their id.
        """
        kwargs['key'] = lambda s: s.last_update
        return super().sort(**kwargs)

    def pretty(self, **kwargs):
        kwargs['format_item'] = lambda item: (
            item.name,
            item.last_update,
            item.meijumi_id,
            item.url
        )
        return super().pretty(**kwargs)

    def valid_shows(self):
        return list(filter(
            lambda item: item.name and item.last_update,
            self.data.copy()))

    def print_latest(self, count):
        valid_shows = self.valid_shows()
        data = sorted(
            valid_shows,
            key=lambda item: item.last_update,
            reverse=True)
        self.pretty_print(data=data, count=count)
