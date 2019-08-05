#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script reads the input data set, cleans the needed values and formats them
as JSON to be inserted later into MongoDB.
"""

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

from cep import clean_CEP, is_CEP
from cities import clean_city, is_city
from suburb import clean_suburb, is_suburb
from house_numbers import clean_house_number, is_house_number
from street_names import clean_street_name, is_street_name
from elevation import clean_elev, is_elevation
from opening_hours import clean_opening_hours, is_opening_hours
from phone_numbers import clean_phone, is_phone


# filename = 'Juiz de Fora Region.osm'
filename = 'sample.osm'


CREATED = [ 'version', 'changeset', 'timestamp', 'user', 'uid']
POSITION = [ 'lat', 'lon' ]



def shape_element(element):

    node = {}

    if element.tag == "node" or element.tag == "way" or element.tag == "relation":

        node['element_type'] = element.tag

        # Parse the top level element attributes
        for attrib, value in element.attrib.items():
            if attrib in CREATED:
                if 'created' not in node.keys():    # key is still not in node
                    node['created'] = {}
                node['created'][attrib] = value
            elif attrib in POSITION:
                if 'pos' not in node.keys():    # key is still not in node
                    node['pos'] = [None, None]
                if attrib == 'lat':
                    node['pos'][0] = float(value)
                else:   # attrib == 'lon'
                    node['pos'][1] = float(value)
            else:   # all other attributes
                node[attrib] = value

        # Now let's parse the subtree
        for sub_element in element.iter():
            if sub_element.tag == 'tag':
                k, v = sub_element.attrib['k'], sub_element.attrib['v']

                if ':' in k:    # Process subfields
                    k_fields = k.split(':')

                    if k_fields[0] == 'addr':
                        k_fields[0] = 'address'

                    # Sometimes there are single elements and elements with subelems
                    # with the same name. e.g. 'name' and 'name:pt'.
                    # If that happens we will convert the field into a dict with
                    # the single element value under a key called 'base'
                    if k_fields[0] in node.keys():
                        if type(node[k_fields[0]]) != dict:
                            single_elem_v = node[k_fields[0]]
                            node[k_fields[0]] = {}
                            node[k_fields[0]]['base'] = single_elem_v
                    else:
                        node[k_fields[0]] = {}


                    if is_CEP(sub_element):
                        v = clean_CEP(v)
                    elif is_city(sub_element):
                        v = clean_city(v)
                    elif is_suburb(sub_element):
                        v = clean_suburb(v)
                    elif is_house_number(sub_element):
                        v = clean_house_number(v)
                    elif is_street_name(sub_element):
                        v = clean_street_name(v)
                    elif is_phone(sub_element):
                        v = clean_phone(v)

                    node[k_fields[0]][k_fields[1]] = v

                else:   # Process regular fields
                    if is_elevation(sub_element):
                        k = 'elevation'
                        v = clean_elev(v)
                    elif is_opening_hours(sub_element):
                        v = clean_opening_hours(v)
                    elif is_phone(sub_element):
                        v = clean_phone(v)

                    node[k] = v

            elif sub_element.tag == 'nd':
                if 'node_refs' not in node.keys():
                    node['node_refs'] = []
                node['node_refs'].append(sub_element.attrib['ref'])

            elif sub_element.tag == 'member':
                if 'member' not in node.keys():
                    node['member'] = {}
                for k, v in sub_element.attrib.iteritems():
                    if k not in node['member'].keys():
                        node['member'][k] = []
                    else:
                        if v not in node['member'][k]:
                            node['member'][k].append(v)

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


def main():
    process_map(filename, pretty=False)

if __name__ == '__main__':
    main()