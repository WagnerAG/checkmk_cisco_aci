#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError
from collections import defaultdict
from os.path import isfile
from typing import List, Dict
from subprocess import check_call
import re


DATA_REGEX: str = r'^\s*(?P<value>[0-9]*)\s(?P<key>.*)$'


def __dir_path(path):
    if isfile(path):
        return path
    else:
        raise ArgumentTypeError(f"readable_stats_file:{path} is not a valid file path")


def parse_args() -> str:
    parser = ArgumentParser()
    parser.add_argument('--stats-file', type=__dir_path, required=False,
                        help='specify custom file name for rndc stats file')
    args = parser.parse_args()

    stats_file: str = 'output/named.stats'
    if args.stats_file is not None:
        stats_file = args.stats_file

    return stats_file


def trigger_rndc_stats(stats_file_path: str) -> None:
    check_call(['mv', stats_file_path, f'{stats_file_path}.old'])
    check_call(['rndc', 'stats'])


def read_stats_file(stats_file_path: str) -> List[str]:
    with open(stats_file_path, 'r') as fp:
        return [line.strip() for line in fp.readlines()]


def split_sections(rndc_stats: List[str]) -> Dict[str, List[str]]:
    """transform raw input from the stats file from named into groups stored in a dict"""
    sections: defaultdict = defaultdict(list)
    section: str = ''
    data_regex = re.compile(DATA_REGEX)

    for line in rndc_stats:
        if line.startswith(('+++ ', '[', '---')):
            continue
        elif line.startswith('++ ') and line.endswith(' ++'):
            section = line.strip('+ ')
        else:
            matches = data_regex.match(line)
            value: str = matches.group('value')
            key: str = matches.group('key')

            sections[section].append(f'{key};{value}')

    return dict(sections)


def __write_section_header(section_name: str) -> None:
    print(f'<<<bind_stats_{section_name}:sep({ord(";")})>>>')


def write_section(sections: Dict[str, List[str]]) -> None:
    for section, values in sections.items():
        section_name = section.lower().replace(' ', '_').replace('/', '')
        __write_section_header(section_name)
        for value in values:
            print(value)


def main():
    stats_file: str = parse_args()
    trigger_rndc_stats(stats_file)
    rndc_stats = read_stats_file(stats_file)
    sections: Dict[str, List[str]] = split_sections(rndc_stats)
    write_section(sections)


if __name__ == '__main__':
    main()
