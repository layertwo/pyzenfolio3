from datetime import datetime
import json

from pyzenfolio3.exceptions import ConfigError

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# TODO do we need a class for this?
class ConvertToDateTime:
    """
    Finds all DateTime instances and converts to datetime objects.
    """
    def find_and_convert_dates(self, root, items):
        for k, v in items:
            if isinstance(v, dict):
                if '$type' in v and v['$type'] == 'DateTime':
                    root[k] = datetime.strptime(v['Value'], DATETIME_FORMAT)
                else:
                    self.find_and_convert_dates(v, v.items())
            elif isinstance(v, (list, tuple)):
                self.find_and_convert_dates(v, enumerate(v))

    def __call__(self, data):
        if hasattr(data, 'items'):
            self.find_and_convert_dates(data, data.items())
        return data


convert_to_datetime = ConvertToDateTime()


def read_config(config_file):
    with open(config_file, 'rb') as fid:
        data = fid.read().decode('utf-8')
        try:
            return json.loads(data)
        except ValueError as config_value_error:
            raise ConfigError('Could not open config file') from config_value_error
