#!/usr/bin/env python

import string

PREFIX_COUNTRY = 'TH'
PREFIX_WAREHOUSE = '01'
PREFIX_YEAR = '15'

def __base36encode(number):
    alphabet = '0123456789' + string.ascii_lowercase
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]

def __base36decode(number):
    return int(number,36)

def get_next_uid(current_uid=None):
    prefix = '{}{}{}'.format(PREFIX_COUNTRY, PREFIX_WAREHOUSE, PREFIX_YEAR)
    if current_uid:
        partial_uid = current_uid[len(prefix):]
        next_uid = __base36decode(partial_uid)
        return '{}{}'.format(prefix, __base36encode(next_uid + 1).zfill(5))
    else:
        return '{}00001'.format(prefix)
