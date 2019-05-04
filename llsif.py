# coding=utf-8
"""
llsif.py - Sopel Love Live! School Idol Festival module
Copyright 2019 dgw
Licensed under the Eiffel Forum License 2

https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import re

import requests

from sopel.logger import get_logger
from sopel import module


API_BASE = 'https://schoolido.lu/api/'
CARD_API = API_BASE + 'cards/'

LATEST_CARD_PARAMS = {
    'ordering': '-id',
    'page_size': 1,
    'japan_only': False,
}

CARD_SEARCH_PARAMS = {
    'page_size': 1,
}


LOGGER = get_logger(__name__)


class APIError(Exception):
    pass


def _api_request(url, params):
    try:
        r = requests.get(url=url, params=params,
                         timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        raise APIError("Connection timed out.")
    except requests.exceptions.ConnectionError:
        raise APIError("Couldn't connect to server.")
    except requests.exceptions.ReadTimeout:
        raise APIError("Server took too long to send data.")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise APIError("HTTP error: " + e.message)
    try:
        data = r.json()
    except ValueError:
        raise APIError("Couldn't decode API response: " + r.content)

    return data


@module.commands('sifcard')
@module.example('.sifcard')
@module.example('.sifcard jp')
@module.example('.sifcard 123')
def sif_card(bot, trigger):
    """Fetch LLSIF EN/WW card information."""
    arg = trigger.group(2)
    if arg is None or arg.lower() in ['en', 'ww']:
        params = LATEST_CARD_PARAMS
        prefix = "Latest SIF EN/WW card: "
    elif arg.lower() == 'jp':
        params = LATEST_CARD_PARAMS.copy()
        del params['japan_only']
        prefix = "Latest SIF JP card: "
    else:
        if re.search(r'[^\d]', arg):
            bot.reply("I can only search by card ID number right now. :(")
            return
        params = CARD_SEARCH_PARAMS.copy()
        params.update({'ids': trigger.group(2)})
        prefix = ""

    try:
        data = _api_request(CARD_API, params)
    except APIError as err:
        bot.say("Sorry, something went wrong with the card API.")
        LOGGER.exception("LLSIF API error!")
        return

    try:
        card = data['results'][0]
    except IndexError:
        bot.reply("No card found!")
        return

    card_id = card['id']
    character = card['idol']['name']
    attribute = card['attribute']
    rarity = card['rarity']
    released = card['release_date']
    link = card['website_url'].replace('http:', 'https:', 1)

    bot.say("{}{} {} {} (#{}), released {} — {}"
            .format(prefix, character, attribute, rarity, card_id, released, link))