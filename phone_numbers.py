#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is used to inspect phone numbers, and
to define a function to clean the incorrect values found.
"""

import main_audit
import re


def clean_phone(phone_number):
    """Standardize format for phone numbers: +XXXXXXXXXXXX.
    Returns either a list of cleaned phone numbers or None
    if phone number is invalid."""

    phones = phone_number.split(';')
    cleaned_phones = []

    for phone in phones:

        if phone.isalpha():
            return None
        else:
            # Remove some unwanted characters
            phone = re.sub('[ \.\-()]', '', phone)

            if not phone.startswith('0800'):
                if phone.startswith('0'):
                    phone = phone[1:]
                elif phone.startswith('55'):
                    phone = '+' + phone
                elif re.search('^\d{10,11}$', phone):
                    phone = '+55' + phone

            cleaned_phones.append(phone)

    return cleaned_phones


def is_phone(elem):
    """Determine if current element (which must have k, v attributes) corresponds
    to phone numbers."""
    return elem.get('k') == 'contact:phone' or elem.get('k') == 'phone'


def main():
    all_kv = main_audit.get_all_tag_kv_from_file(main_audit.filename)

    values = sorted([v for v in all_kv['contact:phone']] + [v for v in all_kv['phone']])
    for value in values:
        cleaned_values = clean_phone(value)
        if cleaned_values == None:
            print value + " / Invalid phone number"
        elif len(cleaned_values) == 1 and value != cleaned_values[0]:
            print value + " / " + cleaned_values[0]
        elif len(cleaned_values) > 1:
            print value + " / " + "; ".join(cleaned_values)


if __name__ == '__main__':
	main()