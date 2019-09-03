#!/usr/bin/env python2

'''
    file name:      utilityFunctions.py
    authors:        Imtiaz Karim (karim7@purdue.edu), Fabrizio Cicala (fcicala@purdue.edu)
    python version: python 2.7.15
'''

import random


def print_on_file(lst):
    with open("mutation_fuzzing_commands","w") as f:
        for el in lst:
            f.write(str(el)+'\n')


def average(lst):
    return sum(lst) / len(lst)


def remove_elements(lst1, lst2):
    new_list = []
    for e in lst1:
        if e not in lst2:
            new_list.append(e)
    return new_list


# Method that returns a random number between 0 and faces
def flip_coin(faces=1):
    return random.randint(0, faces) if faces > 0 else random.randint(0, 1)


# Method that returns a copy of the input list (useful to avoid reference issues)
def copy_list (lst):
    new_list = []
    for el in lst:
        if isinstance(el, type({})):
            new_list.append(copy_dict(el))
        elif isinstance(el, type([])):
            new_list.append(copy_list(el))
        else: 
            new_list.append(el)
    return new_list


# Method that returns a copy of the input dictionary (useful to avoid reference issues)
def copy_dict (dict):
    new_dict = {}
    for k in dict.keys():
        if isinstance(dict[k], type({})):
            new_dict[k] = copy_dict(dict[k])
        elif isinstance(dict[k], type([])):
            new_dict[k] = copy_list(dict[k])
        else:
            new_dict[k] = dict[k]
    return new_dict


# Method that prints a list
def print_list(lst):
    for el in lst:
        print (el)


def print_grammars(gram_list):
    for gram in gram_list:
        print ('Grammar: ', gram['cmd'], gram['struct'], ', Score: ', gram['score'])


def print_grammars_in_set(gram_set):
    for gram in gram_set:
        print gram


def sorted_insert(gram_list, gram):
    if len(gram_list) == 0:
        gram_list.append(gram)
    else:
        for i in range(len(gram_list)):
            if gram['score'] >= gram_list[i]['score']:
                gram_list.insert(i, gram)
                return
        gram_list.append(gram)


def set_sorted_insert(set_list, set_and_score):
    if len(set_list) == 0:
        set_list.append(set_and_score)
    else:
        for i in range(len(set_list)):
            if set_and_score['score'] >= set_list[i]['score']:
                set_list.insert(i, set_and_score)
                return
        set_list.append(set_and_score)


def gram_sorted_insert(gram_list, gram):
    if len(gram_list) == 0:
        gram_list.append(gram)
    else:
        for i in range(len(gram_list)):
            if gram['score'] >= gram_list[i]['score']:
                gram_list.insert(i, gram)
                return
        gram_list.append(gram)


def build_string_gram_cmd(gram, cmd):
    cmd_line = 'Command: ' + str(cmd) + '\n\n'
    gram_line = 'Grammar:\n'
    for field in gram:
        value = 'AT' + str(gram[field]) if field == 'cmd' else str(gram[field])
        gram_line += '\t' + str(field) + ': ' + value + '\n'
    return gram_line + cmd_line


def build_string_set_gram_cmd(gram_set, cmd):
    cmd_line = 'Commands: \n'
    for c in list(cmd):
        cmd_line += str(c) + '\n'
    cmd_line += '\n\n'
    if gram_set is not None:
        gram_line = 'Grammars:\n'
        for gram in gram_set:
            for field in gram:
                value = 'AT' + str(gram[field]) if field == 'cmd' else str(gram[field])
                gram_line += '\t' + str(field) + ': ' + value + '\n'
            gram_line += '\n'
        return gram_line + cmd_line
    return cmd_line
