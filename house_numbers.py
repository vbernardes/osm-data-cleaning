#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect house numbers, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re


def clean_house_number(num):
    """Standardize format for house numbers."""

    if re.search('[Ss]/.*[Nn]', num):    # "sem número" (has no house number)
        num = 's/n'
    elif re.search('km', num):    # capitalize km
        num = num.capitalize()
    else:
        num = num.replace('.', '')    # remove periods in numbers

    return num


def is_house_number(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to a house number."""
    return elem.get('k') == 'addr:housenumber'


def main():
    all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

    values = sorted([v for v in all_kv['addr:housenumber']])
    main_audit.compare_clean_and_unclean(values, clean_house_number)


if __name__ == '__main__':
	main()