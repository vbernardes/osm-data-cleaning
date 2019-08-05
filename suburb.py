#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect suburb names, and
to define a function to clean the incorrect values found.
"""

import main_audit
from main_audit import remove_extra_spaces


def clean_suburb(sub):
    sub = sub[0].upper() + sub[1:]
    return remove_extra_spaces(sub)


def is_suburb(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to a suburb name."""
    return elem.get('k') == 'addr:suburb'


def main():
    all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

    values = sorted([v for v in all_kv['addr:suburb']])
    main_audit.compare_clean_and_unclean(values, clean_suburb)


if __name__ == '__main__':
	main()