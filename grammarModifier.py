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
    #print ('--- gram_crossover method')
    gram_struct = cmd_gram['struct']
    if len(gram_struct) > 2:
        start = 0 if move_command == 1 else 2
        i, j = random.randint(start, len(gram_struct) - 1), random.randint(start, len(gram_struct) - 1)
        gram_struct[i], gram_struct[j] = gram_struct[j], gram_struct[i]
    return cmd_gram


def add_field(cmd_gram):
    #print ('--- add_field method')
    gram_struct = cmd_gram['struct']
    possible_elements = utilityFunctions.remove_elements(cmd_gram.keys(), ['struct', 'arg', 'separator', 'score'])
    missing_elements = setdiff1d(possible_elements, gram_struct)
    if len(missing_elements) > 0:
        gram_struct.append(random.choice(missing_elements))
    
    else:
        cmd_gram['struct'].append('random')
        cmd_gram['arg'].append('random')
        cmd_gram['random'] = {
            "type": "string",
            "length": 5
        } 
        try:
            cmd_gram['separator']
        except (KeyError):     # there is no separator, probably due to the fact that there is one ore less argument
            cmd_gram['separator'] = ','
    


def remove_field(cmd_gram, move_command):
    #print ('--- remove_field method')
    gram_struct = cmd_gram['struct']
    if len(gram_struct) > 2:
        start = 0 if move_command == 1 else 2
        gram_struct.pop(random.randint(start, len(gram_struct) - 1))


# Method that takes as input a list of elements and add/delete an element to/from that list
# # input: cmd_gram = detailed grammar dictionary
def gram_random_add_delete(cmd_gram, move_command=0):
    #print ('--- gram_random_add_delete method')
    gram_struct = cmd_gram['struct']
    if len(gram_struct) < 2 or utilityFunctions.flip_coin() == 0:
        add_field(cmd_gram)
    else:
        remove_field(cmd_gram, move_command)


# Method that take as input a grammar and modify one of the arguments
# in the grammar in order to generate an invalid AT command
# # input: cmd_gram = detailed grammar dictionary
''' NO LONGER USED '''
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


# Method that negates the condition associated to a field. 
# For instance: the field is an integer between 1 and 10, the method changes the range (below 1 or above 10)
def negate_condition(cmd_gram):
    #print('--- negate_condition method')
    arg_in_struct = []
    for el in cmd_gram['arg']:
        if el in cmd_gram['struct']:
            arg_in_struct.append(el)

    if len(arg_in_struct) > 0:
        arg_name = random.choice(arg_in_struct)
        arg = cmd_gram[arg_name]
        type = arg['type']

        if type == 'digit' or type == 'letters' or type == 'string':    # condition: length - int
            half_len, double_len = (arg['length'] / 2), (arg['length'] * 2)
            arg['length'] = double_len if half_len < 2 else random.choice([half_len, double_len])

        elif type == 'ranged':    # condition: range - [int, int]
            start, end = arg['range'][0], arg['range'][1]
            arg['range'] = random.choice([[end + 1, end + 100], [start - 100, start - 1]])

        elif type == 'fixed':    # condition: values - [str, str, ... , str]
            new_value = ''.join(
                random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(10))
            arg['values'].append(new_value)

        elif type == 'immutable':     # condition: immutable_value - str
            pass
        else:
            raise Exception("Error: unknow argument type")





# Method that tries to restore a 'fixed'/'ranged' type in the case it was negate in a previous iteration
# This leverages the fact that we do not delete the field 'values'/'range' when negating the type
def try_restore_type(arg, type):
    if utilityFunctions.flip_coin() == 1:
        try:
            arg['values']
            arg['type'] = random.choice(['string', 'letters', 'fixed'])    
        except (KeyError):
            try:
                arg['range']
                arg['type'] = random.choice(['string', 'letters', 'ranged'])
            except (KeyError):
                if type == 'digit':
                    arg['type'] = random.choice(['string', 'letters'])
                elif type == 'letters':
                    arg['type'] = random.choice(['string', 'digit'])
                elif type == 'string':
                    pass
    else:
        if type == 'digit':
            arg['type'] = random.choice(['string', 'letters'])
        elif type == 'letters':
            arg['type'] = random.choice(['string', 'digit'])
        elif type == 'string':
            pass
        


# Method that negates the type associated to a field.
# For instance: the field is an integer, the method converts it into a string
def negate_type(cmd_gram):
    #print ('--- negate_type method')
    arg_in_struct = []
    for el in cmd_gram['arg']:
        if el in cmd_gram['struct']:
            arg_in_struct.append(el)

    if len(arg_in_struct) > 0:
        arg_name = random.choice(arg_in_struct)
        arg = cmd_gram[arg_name]
        type = arg['type']

        if type == 'digit' or type == 'letters' or type == 'string':
            try_restore_type(arg, type)

        elif type == 'ranged' or type == 'fixed':
            arg['type'] = random.choice(['string', 'digit', 'letters'])
            arg['length'] = random.randint(0, 100)

        elif type == 'immutable': # cannot change immutable
            pass
        else:
            raise Exception("Error: unknow argument type")


# Method that negates the condition associated to a field and set value of the filed to corner case values
# E.g., max integer, min integer, etc.
def fixed_integers(cmd_gram):
    #print ('--- fixed_integers method')
    arg_in_struct = []
    for el in cmd_gram['arg']:
        if el in cmd_gram['struct']:
            arg_in_struct.append(el)

    if len(arg_in_struct) > 0:
        arg_name = random.choice(arg_in_struct)
        arg = cmd_gram[arg_name]
        type = arg['type']

        if type == 'digit':
            arg['type'] = 'fixed'
            arg['values'] = [float('inf'), float('-inf')]
        if type == 'fixed':
            arg['values'].append([float('inf'), float('-inf')])
        if type == 'ranged':
            arg['range'] = [float('inf'), float('-inf')]






# Method that alters the symbols used for connecting grammars and fields with grammars
def alter_connectors(cmd_gram):
    #print ('--- alter_connectors method')
    try:
        cmd_gram['separator']
        cmd_gram['separator'] = random.choice(string.punctuation)
    except (KeyError):
        pass
    



# settings: [feedback, crossover, add_field, remove_field, negate_condition, negate_type, fixed_integers, alter_connectors]
#   where each of the fields can be 0/1
def modify_grammar(cmd_gram, settings, move_command=0):
    #print ('--- modify_grammar')
    settings =  settings.split(',')
    if settings[1] == '1': # crossover
        gram_crossover(cmd_gram, move_command)
    
    if settings[2] == '1' and settings[3] == '1': # both add_field and remove_field
        if utilityFunctions.flip_coin() == 1:
            gram_random_add_delete(cmd_gram, move_command)
    elif settings[2] == '1' and settings[3] == '0': # add_field
        if utilityFunctions.flip_coin() == 1:
            add_field(cmd_gram)
    elif settings[2] == '0' and settings[3] == '1': # remove_field
        if utilityFunctions.flip_coin() == 1:
            remove_field(cmd_gram, move_command)
    
    if settings[4] == '1': # negate_condition
        if utilityFunctions.flip_coin() == 1:
            negate_condition(cmd_gram)
    
    if settings[5] == '1': # negate_type
        if utilityFunctions.flip_coin() == 1:
            negate_type(cmd_gram)
    
    if settings[6] == '1': # fixed_integers
        if utilityFunctions.flip_coin() == 1:
            fixed_integers(cmd_gram)
    
    if settings[7] == '1': # alter_connectors
        if utilityFunctions.flip_coin() == 1:
            alter_connectors(cmd_gram)

''' 

Fuzzing strategies

 # Crossover
    - single-point crossover
    - two-point crossover

# Mutation
    - field addition
    - field trimming
    - condition negation
    - type negation
    - fixed integers (max_int, min_int)
    - connector change (wwith specific symbols)

'''

