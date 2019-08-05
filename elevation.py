#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect elevation values, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re


def clean_elev(elev):
    """Standardize formatting for elevation values by removing measurement units."""

    elev_re = re.compile('\d+')
    return int(elev_re.search(elev).group())


def is_elevation(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to an elevation value."""
    return elem.get('k') == 'ele'


def main():
    all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

    values = sorted([v for v in all_kv['ele']])

    for elevation in values:
        cleaned_elev = clean_elev(elevation)
        if elevation != str(cleaned_elev):
            print elevation + " / " + str(cleaned_elev)


if __name__ == '__main__':
	main()