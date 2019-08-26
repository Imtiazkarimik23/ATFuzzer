#!/usr/bin/env python2.7

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
        print el


def print_grammars(gram_list):
    for gram in gram_list:
        print 'Grammar: ', gram['struct'],', Score: ', gram['score']


def sorted_insert(gram_list, gram):
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