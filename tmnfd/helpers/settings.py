from helpers.config import get_config
import xml.etree.ElementTree as ET
import os


class DedicatedCfg():
    def __init__(self):
        self.tree = ET.parse(get_config()['config_path'])

    def save(self):
        self.tree.write(get_config()['config_path'], encoding='utf-8', xml_declaration=True, short_empty_elements=False)

    def set_name(self, name):
        self.tree.find('server_options').find('name').text = name

    def get_name(self):
        return self.tree.find('server_options').find('name').text

    def set_xmlrpc(self, port=5000, allowremote=True):
        self.tree.find('system_config').find('xmlrpc_port').text = str(port)
        self.tree.find('system_config').find('xmlrpc_allowremote').text = str(allowremote)

    def get_xmlrpc(self):
        return (self.tree.find('system_config').find('xmlrpc_port').text, self.tree.find('system_config').find('xmlrpc_allowremote').text)

    def set_laddermode(self, mode='inactive'):
        self.tree.find('server_options').find('ladder_mode').text = mode

    def get_laddermode(self):
        return self.tree.find('server_options').find('ladder_mode').text


class MatchSettings():
    def __init__(self, name):
        self.name = name
        self.tree = ET.parse(os.path.join(get_config()['match_settings'], name))
        self.tree.find('gameinfos').find('game_mode').text = '1'
        self.tree.find('filter').find('is_lan').text = '1'
        self.tree.find('filter').find('is_internet').text = '0'

    def save(self, activate=False):
        self.tree.write(os.path.join(get_config()['match_settings'], self.name), encoding='utf-8', xml_declaration=True, short_empty_elements=False)
        if activate:
            self.tree.write(get_config()['active_path'], encoding='utf-8', xml_declaration=True, short_empty_elements=False)

    def set_random_map_order(self, random=False):
        self.tree.find('filter').find('random_map_order').text = ('1' if random else '0')

    def get_random_map_order(self):
        return (True if self.tree.find('filter').find('random_map_order').text == '1' else False)

    def get_challenges(self):
        result = list()
        for c in self.tree.findall('challenge'):
            ident = c.find('ident').text
            path = c.find('file').text
            result.append((ident, path))
        return result
