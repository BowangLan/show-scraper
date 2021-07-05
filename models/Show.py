import re
from time import perf_counter
from datetime import date, datetime
from requests_html import HTMLSession
from tabulate import tabulate
from .base import ObjectModelBase


class Show(ObjectModelBase):
    def __init__(self, **kwargs) -> None:
        params = ['name', 'original_name',
                  'meijumi_id', 'url', 'img', 'last_update']
        for param in params:
            kwargs[param] = kwargs[param] if kwargs.get(param) else None
        super().__init__(**kwargs)
        self.meijumi_id = kwargs['meijumi_id']
        self.url = kwargs['url']
        self.last_update = kwargs['last_update']

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, value: str):
        if value:
            self.data['name'] = value

    @property
    def original_name(self):
        return self.data['original_name']

    @original_name.setter
    def original_name(self, value: str):
        if value:
            self.data['original_name'] = value

    @property
    def last_update(self):
        return self.data.get('last_update')

    @last_update.setter
    def last_update(self, value):
        if value:
            if type(value) == str:
                self.data['last_update'] = datetime.strptime(
                    value, '%Y-%m-%d').date()
            elif type(value) == date:
                self.data['last_update'] = value

    @property
    def url(self):
        if self.data.get('url'):
            return self.data['url']
        else:
            return ''

    @url.setter
    def url(self, value):
        if value:
            self.data['url'] = value
            self.data['meijumi_id'] = re.findall(
                u'https://www.meijumi.net/(\d+)\.html', value)[0]

    @property
    def meijumi_id(self):
        if self.data.get('meijumi_id'):
            return self.data['meijumi_id']
        else:
            return ''

    @meijumi_id.setter
    def meijumi_id(self, value: str):
        if value:
            self.data['meijumi_id'] = value
            self.data['url'] = u'https://www.meijumi.net/{}.html'.format(value)

    @property
    def img(self):
        if self.data.get('img'):
            return self.data['img']
        else:
            return ''

    @img.setter
    def img(self, value: str):
        self.data['img'] = value

    def __hash__(self) -> int:
        return hash((self.meijumi_id))

    def __str__(self) -> str:
        return "({}){}".format(self.meijumi_id, self.name)

    def __repr__(self) -> str:
        return '<Show name="{}" url="" >'.format(self.name, self.url)

    def __eq__(self, o: object) -> bool:
        return self.meijumi_id == o.meijumi_id

    def __ne__(self, o: object) -> bool:
        return self.meijumi_id != o.meijumi_id

    def json(self):
        return {
            'name': self.name,
            'original_name': self.original_name,
            'meijumi_id': self.meijumi_id,
            'img': self.img,
            'last_update': str(self.last_update) if self.last_update else ''
        }

    def pretty(self):
        output = ''
        row_names = ['Name', 'Meijumi ID', 'Last Update', 'Link']
        max_length = max([len(i) for i in row_names]) + 3
        row_names = ['{}:'.format(i).ljust(max_length) for i in row_names]
        output += '{} {}\n'.format(row_names[0], self.name)
        output += '{} {}\n'.format(row_names[1], self.meijumi_id)
        output += '{} {}\n'.format(row_names[2], self.last_update)
        output += '{} {}\n'.format(row_names[3], self.url)
        return output

    def merge(self, o):
        self.img = o.img if o.img else self.img
        self.original_name = o.original_name if o.original_name else self.original_name
        if o.last_update:
            if self.last_update and o.last_update > self.last_update:
                self.last_update = o.last_update
            elif not self.last_update:
                self.last_update = o.last_update

    def get_show(self):
        """
        """
        with HTMLSession() as s:
            tic = perf_counter()
            res = s.get(self.url, verify=False)

        content = res.html.find('.single-content')[0].html

        # get the title
        # title = re.findall(
        #     u'《(.+?)》', res.html.find('h1.entry-title')[0].html)[0]
        name = re.findall(
            u'《(.+?)》', res.html.find('h1.entry-title')[0].html
        )
        if name:
            self.name = name[0]

        # get the original title
        original_name = re.findall(
            u'英文全名(.+?)(?:\s*?\(\d{4}\))', content
            # u'英文全名(.+?)(?:\sSeason\s\d{1,2})?(?:\s\s\(\d{4}\))', content
        )
        self.original_name = original_name[0] if original_name != [] else ''

        # get the img url
        self.img = re.findall(u'<img.+?src="(.+?)".+?>', content)[0]

        print("{} updated in {:0.4f}".format(
            self.__str__(), perf_counter() - tic))
