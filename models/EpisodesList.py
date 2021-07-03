from .base import ObjectListBase
from .Episodes import Episodes


class EpisodesList(ObjectListBase):
    def __init__(self, **kwargs) -> None:
        kwargs['child_class'] = Episodes
        super().__init__(**kwargs)

    def pprint_show_episode_output(self):
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
        for block in self.data:
            print_block(block)
