#!/usr/bin/env python2

'''
    file name:      grammarModifier.py
    authors:        Imtiaz Karim (karim7@purdue.edu), Fabrizio Cicala (fcicala@purdue.edu)
    python version: python 2.7.15
'''

import random
import string
import utilityFunctions
from numpy import setdiff1d


def gram_crossover(cmd_gram, move_command=0):
    gram_struct = cmd_gram['struct']
    if len(gram_struct) > 2:
        start = 0 if move_command == 1 else 2
        i, j = random.randint(start, len(gram_struct) - 1), random.randint(start, len(gram_struct) - 1)
        gram_struct[i], gram_struct[j] = gram_struct[j], gram_struct[i]
    return cmd_gram


def add_field(cmd_gram):
    gram_struct = cmd_gram['struct']
    possible_elements = utilityFunctions.remove_elements(cmd_gram.keys(), ['struct', 'arg', 'separator', 'score'])
    missing_elements = setdiff1d(possible_elements, gram_struct)
    if len(missing_elements) > 0:
        gram_struct.append(random.choice(missing_elements))


def remove_field(cmd_gram, move_command):
    gram_struct = cmd_gram['struct']
    if len(gram_struct) > 2:
        start = 0 if move_command == 1 else 2
        gram_struct.pop(random.randint(start, len(gram_struct) - 1))


# Method that takes as input a list of elements and add/delete an element to/from that list
# # input: cmd_gram = detailed grammar dictionary
def gram_random_add_delete(cmd_gram, move_command=0):
    gram_struct = cmd_gram['struct']
    if len(gram_struct) < 2 or utilityFunctions.flip_coin() == 0:
        add_field(cmd_gram)
    else:
        remove_field(cmd_gram, move_command)


# Method that take as input a grammar and modify one of the arguments
# in the grammar in order to generate an invalid AT command
# # input: cmd_gram = detailed grammar dictionary
def make_gram_invalid(cmd_gram):
    arg_in_struct = []
    for el in cmd_gram['arg']:
        if el in cmd_gram['struct']:
            arg_in_struct.append(el)

    if len(arg_in_struct) > 0:
        arg_name = random.choice(arg_in_struct)
        arg = cmd_gram[arg_name]
        type = arg['type']

        if type == 'digit' or type == 'letters':
            half_len, double_len = (arg['length'] / 2), (arg['length'] * 2)
            if utilityFunctions.flip_coin(2) > 0:
                if half_len < 2:
                    arg['length'] = double_len
                elif double_len > 1000:
                    arg['length'] = half_len
                else:
                    arg['length'] = random.choice([half_len, double_len])
            else:
                arg['type'] = 'string'

        elif type == 'string':
            half_len, double_len = (arg['length'] / 2), (arg['length'] * 2)
            if half_len < 2:
                arg['length'] = double_len
            elif double_len > 1000:
                arg['length'] = half_len
            else:
                arg['length'] = random.choice([half_len, double_len])

        elif type == 'ranged':
            start, end = arg['range'][0], arg['range'][1]
            arg['range'] = random.choice([[end + 1, end + 100], [start - 100, start - 1]])

        elif type == 'fixed':
            if utilityFunctions.flip_coin() == 0:
                new_value = ''.join(
                    random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(10))
                arg['values'].append(new_value)
            else:
                cmd_gram[arg_name] = {"type": "string", "length": 10}

        elif type == 'immutable':
            pass
        else:
            raise Exception("Error: unknow argument type")
