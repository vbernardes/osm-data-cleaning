#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect opening hours, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re


def clean_opening_hours(hours):
    """Standardize format for opening hours."""

    one_digit_hour_re = re.compile('(?<!\d)(\d{1})(:\d{2})')
    two_hours_re = re.compile(u'(\d{2}:\d{2})[aàsátée \-]+(\d{2}:\d{2})[Hh]?')

    def add_leading_zero(match_obj):
        return '0'+match_obj.group(1)+match_obj.group(2)

    def standardize_with_dash(match_obj):
        return match_obj.group(1)+'-'+match_obj.group(2)

    hours = one_digit_hour_re.sub(add_leading_zero, hours)
    hours = two_hours_re.sub(standardize_with_dash, hours)

    return hours


def is_opening_hours(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to opening hours."""
    return elem.get('k') == 'opening_hours'


def main():
    all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

    values = sorted([v for v in all_kv['opening_hours']])
    main_audit.compare_clean_and_unclean(values, clean_opening_hours)


if __name__ == '__main__':
	main()