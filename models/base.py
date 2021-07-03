import os
import json
from tabulate import tabulate


class ObjectModelBase(object):
    def __init__(self, **kwargs) -> None:
        self.data = kwargs

    def __getitem__(self, item):
        return self.data[item]

    def json(self):
        pass

    def array(self):
        pass

    def pretty(self):
        pass


class ObjectListBase(object):
    def __init__(self, child_class: object = None, objects: list = [], data: list = [], json_path: str = '', **kwargs) -> None:
        super().__init__(**kwargs)
        self.child_class = child_class
        self.json_path = json_path
        self.data = [self.child_class(**d) for d in data]
        self.load_json()
        if objects:
            self.data = objects

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, subscript):
        return self.data[subscript]

    def __len__(self):
        return len(self.data)

    """
    ###########################################################
    Methods for loading and saving data to and from local files
    ###########################################################
    """

    def load_data(self, data):
        """
        Create a list of specified object(self.child_class) from the json data, and 
        store them as a list in self.data.
        """
        self.data = [self.child_class(**d) for d in data]

    def load_json(self):
        """
        Load the list json data from json file self.json_path
        """
        if self.json_path:
            if os.path.exists(self.json_path):
                with open(self.json_path, encoding='utf-8') as f:
                    data = json.load(f)
                    self.load_data(data)
                    print("{} {}(s) loaded from json file \"{}\"".format(
                        len(self.data), self.child_class.__name__, self.json_path))
            else:
                print("Path \"{}\" does not exist".format(self.json_path))
        else:
            # print("No json path specified")
            pass

    def save(self):
        """
        Save the data into the specified json file. Return the number of object saved if successful,
        else return False.
        """
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                data = [obj.json() for obj in self.data]
                json.dump(data, f)
                return len(data)
        except Exception as e:
            return False

    def append_one(self, obj):
        """
        Append a single object to the list data. 
        Return True if append successfully, False if the object is already in the list data.
        """
        if obj in self.data:
            return False
        else:
            self.data.append(obj)
            return True

    def append_many(self, objects):
        """
        Append a list of potential new objects to the existing data. Add the object to 
        the list data if it is not already in the list data. Return a list of new objects added.
        """
        new_objects = []
        for show in objects:
            result = self.append_one(show)
            if result:
                new_objects.append(show)
        print('{} new objects added to the dataset'.format(len(new_objects)))
        return new_objects

    def unique(self):
        return len(self.data) == len(set(self.data))

    def json(self):
        return [i.json() for i in self.data]

    def pretty(self, start: int = 0, end: int = None, step: int = 1, count: int = None):
        """
        Return a prettified string of the requested data based on the parameters given.

        :param start: int, default 0;
        :param end: int, default the length of the dataset;
        :param step: int, default 1;

        return data range: data[start:end:step]
        """
        end = end if end else len(self.data)
        if count:
            end = start + count
        return tabulate([item.array() for item in self.data[start:end:step]],)

    def pretty_print(self, **kwargs):
        print(self.pretty(**kwargs))
