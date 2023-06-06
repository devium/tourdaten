#!/usr/bin/env python3

import argparse
import dateparser
import datetime
import json
from typing import Dict, List, Tuple

def main():
    args = parse_args()
    log = load_log(args.filename)
    parse_events(log)
    # TODO: stuff
    first_day, last_day = get_date_range(args.year, args.cw)

def parse_args() -> Dict:
    parser = argparse.ArgumentParser(description='Tourdaten')
    parser.add_argument('filename', type=str, help='Matrix JSON log to parse')
    parser.add_argument('cw', type=int, help='Calendar week')
    parser.add_argument('year', nargs='?', default=2023, help='Year')
    args = parser.parse_args()
    return args

def load_log(filename: str) -> Dict:
    with open(filename, 'r') as file:
        return json.load(file)
    
def get_date_range(year: int, week: int) -> Tuple[datetime.datetime, datetime.datetime]:
    first = datetime.datetime.strptime(f'{year}-{week}-1', '%Y-%W-%w').date()
    last = first + datetime.timedelta(days=6)
    return first, last

class Event:
    def __init__(self, title: str, date: datetime.datetime, url: str):
        self.title = title
        self.date = date
        self.url = url

    def __str__(self):
        return f'Event({self.title}, {self.date}, {self.url})'
    
    def __repr__(self):
        return str(self)
    
    @classmethod
    def from_message(cls, message: str) -> 'Event':
        body = message['content']['body']
        lines = body.splitlines()

        title = lines[0]

        lines_as_dates = (dateparser.parse(line, languages=['de']) for line in lines)
        try:
          date = next(date for date in lines_as_dates if date is not None)
        except StopIteration:
          date = None

        url = create_message_url(message)

        return cls(title, date, url)

def parse_events(log: Dict):
    messages = filter_text_messages(log['messages'])
    events = [Event.from_message(message) for message in messages]
    # TEMP
    print('\n'.join(str(event) for event in events))

def filter_text_messages(messages: List[Dict]) -> List[Dict]:
    return [
        message for message in messages
        if message['type'] == 'm.room.message' and
          'msgtype' in message['content'] and
          message['content']['msgtype'] == 'm.text'
    ]

def create_message_url(message):
    return f'https://matrix.to/#/{message["room_id"]}/{message["event_id"]}'

if __name__ == "__main__":
    main()
