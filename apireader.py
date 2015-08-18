#!/usr/bin/env python3

import sys
import os.path
import requests
import json
from argparse import ArgumentParser

DUMP_NAME = "api_data.dump"
DIRECTORY_URI = "https://raw.githubusercontent.com/freifunk/directory.api.freifunk.net/master/directory.json"


def get_api_dict():
    response = requests.get(DIRECTORY_URI)
    api_dict = json.loads(response.text)
    return api_dict


def get_api_data_from_git(api_dict):
    data = dict()
    for community in api_dict:
        api_url = api_dict[community]
        print("Loading {:<20} {} ...".format(community, api_url), file=sys.stderr)
        try:
            response = requests.get(api_url, timeout=2)
            community_api = response.json()
            data[community] = community_api
        except (requests.exceptions.RequestException, ValueError):
            print("Error: Couldn't load api file for {} from {}.".format(community, api_url), file=sys.stderr)

    return data


def get_api_data_from_file(filename):
    with open(filename, 'r') as dump_file:
        api_data = json.load(dump_file)
    return api_data


def get_api_data(api_dict):
    if os.path.isfile("api_data.dump"):
        return get_api_data_from_file(DUMP_NAME)
    else:
        return get_api_data_from_git(api_dict)


def dump_api_data(dest):
    api_dict = get_api_dict()
    api_data = get_api_data_from_git(api_dict)
    with open(dest, "w") as dump_file:
        json.dump(api_data, dump_file)


if __name__ == "__main__":
    PARSER = ArgumentParser(description="Dump freifunk-api data from all communities.")

    PARSER.add_argument("--dest",
                        metavar="FILE", dest="dest",
                        default=DUMP_NAME,
                        help="Filename of the data dump. Default: " +
                             DUMP_NAME)

    ARGS = PARSER.parse_args()

    dump_api_data(ARGS.dest)
