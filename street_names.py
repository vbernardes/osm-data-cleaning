#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect street names, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re
import requests
from bs4 import BeautifulSoup


def get_attrib_values(xpath, elem):
    """Look for xpath in elem and add all corresponding values to a set.
    Expects elements found on xpath to have a 'v' attribute."""

    return_set = set()

    for element in elem.findall(xpath):
        return_set.add(element.get('v'))

    return return_set


def get_street_names_in_way(elem):
    """Look for 'way' elements that are likely streets and return a set of their names."""

    names = set()

    for way in elem.findall('.//way'):
        if way.find('.//tag[@k="highway"]') is not None:
            name_elem = way.find('.//tag[@k="name"]')
            if name_elem is not None:
                names.add(name_elem.get('v'))

    return names



def get_street_types_from_postal():
    """Access the Brazilian Postal Services website and extract official approved
    street name types (e.g. street, avenue etc.)"""
    types = []

    URL = 'http://www.buscacep.correios.com.br/sistemas/buscacep/buscaCep.cfm'

    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    select = soup.find(name='select', attrs={'name':'Tipo'})
    for option in select.find_all(name='option', string=True):
        types.append(option['value'])

    return types


# Set global variable for use in audit + cleaning functions
official_street_types = get_street_types_from_postal()


def clean_name_from_postal(name, city):
    """Access Brazilian Postal Services and check whether the given name
    is a street name. If found, we update the name with its correct complete version.
    Else, return the unchanged name."""

    # Prepare name for form
    prepped_name = name.encode('ISO-8859-1')

    URL = 'http://www.buscacep.correios.com.br/sistemas/buscacep/resultadoBuscaCep.cfm'
    post_data = {
        'UF': 'MG',
        'Localidade': city,
        'Logradouro': prepped_name
    }

    SUCCESS = 'DADOS ENCONTRADOS COM SUCESSO.'
    FAILURE = 'LOGRADOURO NAO ENCONTRADO.'

    r = requests.post(URL, post_data)
    soup = BeautifulSoup(r.text, 'html.parser')

    result_message = soup.find('div', class_='ctrlcontent').find('p').string

    if result_message == SUCCESS:
        table = soup.find(name='table', class_='tmptabela')
        name_found = table.find('td').string   # The first 'td' has what we're looking for
    else:
        return name

    # Some street names have notes after '-'. Remove them
    name_found = name_found.split('-')[0]

    return name_found.strip()



def audit_street_names(names):
    """Receive a list of street names and return some values that could require cleaning."""

    names_to_check = set()

    unwanted_chars_re = re.compile('[;.\-]')

    for name in names:
        first_word = name.split(' ')[0]
        if unwanted_chars_re.search(first_word) is not None or\
           first_word not in official_street_types:
            names_to_check.add(name)

    return names_to_check


def capitalize_proper_name(name):
    """Capitalize proper names according to PT-BR conventions."""

    exceptions = ['do', 'da', 'dos', 'das', 'de', 'o', 'a', 'ao', 'para', 'e', u'à', 's/n']

    words = name.lower().split(' ')
    cap_name = [words[0].capitalize()]
    for word in words[1:]:
        cap_name.append(word.capitalize() if word not in exceptions else word)
    return " ".join(cap_name)


def is_street_name(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to a street name."""

    is_addr_street = elem.get('k') == 'addr:street'
    is_name = elem.get('k') == 'name'
    has_highway_sibling = elem.find('../tag[@k="highway"]')

    return is_addr_street or (is_name and has_highway_sibling)


def clean_street_name(name):

    mapping = {}
    mapping.update(dict.fromkeys(['R.', u'RUa', 'Ru', 'Rua.', u'Rus', u'Ruia'], 'Rua'))
    mapping.update(dict.fromkeys(['Tv.', 'Tracessa', 'Trafessa', 'Travessia', u'Travressa'], 'Travessa'))
    mapping.update(dict.fromkeys([u'Av.', 'Avenido'], 'Avenida'))
    mapping.update(dict.fromkeys(['Estr.'], 'Estrada'))

    name = main_audit.remove_extra_spaces(name)

    # If there's no space after first word, correct it
    no_space_after_street_re = re.compile('^(R\.|Rua)[^ .].*')
    match_no_space = no_space_after_street_re.search(name)
    if match_no_space is not None:
        name = re.sub(match_no_space.group(1), 'Rua ', name)

    # Substitute some typos
    words = name.split(' ')
    if words[0] in mapping.keys():
        name = mapping[words[0]] + ' ' + ' '.join(words[1:])

    # Correct capitalization of uppercase names
    if name.isupper():
        for street_type in official_street_types:
            if name.lower().startswith(street_type.lower()):
                name = capitalize_proper_name(name)

    # Clean highway names
    highway_re = re.compile('(BR|MG|RJ)[ \-] *(\d{3})')
    if highway_re.search(name) is not None:
        name = highway_re.sub(lambda match: match.group(1) + '-' + match.group(2), name)

    return name


def main():
    root = main_audit.get_root(main_audit.filename)
    all_kv = main_audit.get_all_tag_kv(root)

    addrstreet_names = get_attrib_values('.//tag[@k="addr:street"]', root)
    way_street_names = get_street_names_in_way(root)
    all_street_names = sorted(addrstreet_names.union(way_street_names))

    main_audit.compare_clean_and_unclean(all_street_names, clean_street_name)


if __name__ == '__main__':
	main()