#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect all CEP (postal code) values for our data set, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re


def clean_CEP(cep):
    """Correct formatting of the provided CEP (postal code)."""

    #correct_cep = re.compile('\d{5}-\d{3}')
    missing_dash = re.compile('\d{8}')
    extra_period = re.compile('\d{2}\.\d{3}-\d{3}')

    if missing_dash.search(cep):
        cep = cep[:5] + '-' + cep[-3:]
    elif extra_period.search(cep):
        cep = cep[:2] + cep[3:]

    return cep


def is_CEP(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to a CEP (postcode)."""
    return elem.get('k') == 'addr:postcode'


def main():
	all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

	values = sorted([v for v in all_kv['addr:postcode']])
	main_audit.compare_clean_and_unclean(values, clean_CEP)


if __name__ == '__main__':
	main()