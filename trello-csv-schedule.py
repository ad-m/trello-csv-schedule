from __future__ import print_function, unicode_literals

import argparse
import os
import os.path
import re
import sys

import dateutil.parser
import iso8601
import rfc3339
import trello
import unicodecsv as csv
from progress.bar import Bar
from pytz import timezone
from trello import TrelloApi

try:
    import configparser
except:
    from six.moves import configparser


APP_NAME = sys.argv[0]


def parse_trello_board_url(string):
    # https://trello.com/b/jiqjSvq1/oki-wzi
    # jiqjSvq1
    # https://trello.com/b/jiqjSvq1

    if re.match("^([0-9A-Za-z]+)$", string):
        return string
    if '/' in string:
        groups = re.match("trello.com/b/([0-9A-Za-z]+)(/|$)", string)
        if groups:
            return groups.match(1)
    msg = "%r is not a valid URL square" % string
    raise argparse.ArgumentTypeError(msg)


class ScheduleManager(object):
    CONFIG_FILES = [os.path.expanduser("~/trello-schedule.cfg"), "trello-schedule.cfg"]

    def __init__(self, argv):
        self.argv = argv

    def argparse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-g', '--global')

        subparsers = parser.add_subparsers(dest="action")

        import_parser = subparsers.add_parser('sync', help="Import cards from file")
        import_parser.add_argument('board',
                                   help="ID or URL of board",
                                   type=parse_trello_board_url)
        import_parser.add_argument('file',
                                   help="Filename of file with cards",
                                   type=argparse.FileType('rb'))

        export_parser = subparsers.add_parser('download', help="Export cards to file")
        export_parser.add_argument('board',
                                   help="ID or URL of board",
                                   type=parse_trello_board_url)
        export_parser.add_argument('file',
                                   help="Filename of file to write cards",
                                   type=argparse.FileType('wb'))

        init_parser = subparsers.add_parser('setup', help="Perform a initial configuration of tool")
        init_parser.add_argument('-k', '--key', required=True)

        return parser.parse_args(self.argv[1:])

    def find_config_file(self):
        for path in self.CONFIG_FILES:
            if os.path.isfile(path):
                return path
        return None

    def get_client(self):
        client = TrelloApi(self.config.get('Access', 'api_key'),)
        client.set_token(self.config.get('Access', 'token'))
        return client

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILES)
        if not config.has_section("Access"):
            config.add_section("Access")
        return config

    def init(self):
        self.args = self.argparse()
        if self.find_config_file() is None and self.args.action != "setup":
            print("Warning: No init performed. Execute '{} setup'.".format(self.argv[0]))
        self.config = self.get_config()
        getattr(self, self.args.action)()

    def setup(self):
        self.config.set('Access', 'api_key', self.args.key)
        url = trello.get_token_url(APP_NAME, expires="1day", write_access=True)
        print("Please visit '{}' and authorize our application".format(url))
        token = raw_input("Enter a token key: ").strip()
        self.config.set("Access", 'token', token)
        self.config.write(open("trello-schedule.cfg", "wb"))

    def download(self):
        client = self.get_client()
        board = client.boards.get(self.args.board)
        print("Downloading cards from ", board['name'])
        fieldnames = ['id', 'name', 'due', 'idList', 'listName']
        c = csv.DictWriter(self.args.file, fieldnames=fieldnames)
        c.writeheader()
        list_map = {x['id']: x
                    for x in client.boards.get_list(self.args.board)}

        cards = client.boards.get_card(self.args.board)
        bar = Bar('Downloading', max=len(cards))
        for card in cards:
            row = {'id': card['id'],
                   'name': card['name'],
                   'due': self.api_to_file(card['badges']['due']),
                   'idList': card['idList'],
                   'listName': list_map[card['idList']]['name']}
            c.writerow(row)
            bar.next()
        bar.finish()

    def any_changes_cards(self, local, online):
        return any(online[x] != local[x] for x in ['name', 'due', 'idList'])

    def api_to_date(self, value):
        if value:
            return iso8601.parse_date(value)
        else:
            return None

    def api_to_file(self, value):
        return self.api_to_date(value).strftime("%Y.%m.%d %H:%M:%S") if value else ''

    def file_to_date(self, value):
        if value:
            return timezone("Europe/Warsaw").localize(dateutil.parser.parse(value))
        else:
            return None

    def date_to_api(self, value):
        return rfc3339.rfc3339(value) if value else ''

    def date_like(self, a, b):
        if a == b:
            return True
        print(a, b)
        if abs(a - b).total_seconds() > 60:  # accurate to one minute
            return False
        return True

    def sync(self):
        client = self.get_client()
        board = client.boards.get(self.args.board)
        print("Sync cards on ", board['name'])
        cards = list(csv.DictReader(self.args.file))
        cards_online = {card['id']: card
                        for card in client.boards.get_card(self.args.board)}
        bar = Bar('Sync', max=len(cards))
        for card in cards:
            due_online = self.api_to_date(cards_online[card['id']]['due'])
            due_local = self.file_to_date(card['due'])
            if self.date_like(due_online, due_local):
                bar.next()
                print("Skip ", card['name'])
                continue
            print("Update card '{name}'".format(name=card['name']) +
                  " from '{old}' to '{new}".format(old=self.date_to_api(due_online),
                                                   new=self.date_to_api(due_local)))
            client.cards.update_due(card['id'], due_local)
            bar.next()
        bar.finish()


ScheduleManager(sys.argv).init()
