#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect city names, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re


def clean_city(city):

    typos = {
        u'Erália': u'Ervália',
        u'Vicosa': u'Viçosa',
        u'São João del rei': u'São João del-Rei'
    }

    if city in typos.keys():
        city = typos[city]
    else:
        # Remove parentheses
        if '(' in city:
            city, _, _ = city.partition('(')
            city = city.strip()

        # Remove state
        state_re = re.compile('MG|RJ')
        state_match = state_re.search(city)
        if state_match is not None:
            city = state_re.sub('', city)
        city = city[0].upper() + city[1:].strip(' -')

    return city


def is_city(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to a city name."""
    return elem.get('k') == 'addr:city'



def main():
    all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

    values = sorted([v for v in all_kv['addr:city']])
    main_audit.compare_clean_and_unclean(values, clean_city)


if __name__ == '__main__':
	main()