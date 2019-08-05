#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This module contains functions used to read the input file and extract all keys
and values for 'tag' elements. These are the values inspected in search of
cleaning opportunities.
"""

import xml.etree.cElementTree as ET
import re


filename = 'Juiz de Fora Region.osm'


def get_root(filename):
    tree = ET.parse(filename)
    return tree.getroot()



def get_all_tag_kv(root):
    """Get all keys and values from 'tag' elements and return them in a dictionary.
    Each value in the dict is a set containing all values found for that key."""

    dic = {}

    for elem in root.findall('.//tag'):
        k, v = elem.get('k'), elem.get('v')
        if k not in dic.keys():
            dic[k] = set()
        dic[k].add(v)

    return dic


def get_all_tag_kv_from_file(filename):
    root = get_root(filename)
    return get_all_tag_kv(root)


def compare_clean_and_unclean(values, clean_function):
    """Run through all values and execute clean_function for each.
    If the cleaned value differs from the original value, print them."""

    for value in values:
        cleaned_value = clean_function(value)
        if value != cleaned_value:
            print value + " / " + cleaned_value


def remove_extra_spaces(string):
    return re.sub(' {2,}', ' ', string)


def main():
    all_kv = get_all_tag_kv_from_file(filename)

    # Show all keys and values for 'tag' elements
    for k in sorted(all_kv.keys()):
        for v in all_kv[k]:
            print k+': '+v


if __name__ == '__main__':
    main()