#!/usr/bin/env python2

'''
    file name:      inputGen.py
    authors:        Imtiaz Karim (karim7@purdue.edu), Fabrizio Cicala (fcicala@purdue.edu)
    python version: python 2.7.15
'''

import random
import string


semicolon = ';'
# produce a string with a random number of semicolon (1-5)
def random_semicolon():
    semicolon_num = random.randint(1,5)
    return ''.join(semicolon for x in range(semicolon_num))


# produce a random number of maximum length 'value_length'
def random_digits(value_length):
    if value_length<0:
        raise Exception('random_digits error: negative length')
    if value_length == 0:
        value_length = 1
    l = random.randint(1, value_length)
    range_start = 10**(l-1)
    range_end = (10**l)-1
    return str(random.randint(range_start, range_end))


# produce a random string of letters of length 'value_length'
def random_letters(value_length):
    if value_length<0:
        raise Exception('random_letters error: negative length')
    l= 1 if value_length == 1 or value_length == 0 else random.randint(1, value_length)
    return ''.join(random.choice(string.lowercase) for x in range(l))


# produce a random string of numbers, letters and symbols of length 'value_length'
def random_string(value_length):
    if value_length<0:
        raise Exception('random_string error: negative length\n')
    l = 1 if value_length == 1 or value_length == 0 else random.randint(1, value_length)
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(l))


def generate_value(singol_arg):
    type = singol_arg['type']
    if type == 'digit':
        return random_digits(singol_arg['length'])
    elif type == 'letters':
        return random_letters(singol_arg['length'])
    elif type == 'string':
        return random_string(singol_arg['length'])
    elif type == 'ranged':
        start, end = singol_arg['range'][0], singol_arg['range'][1]
        print('#############' + str(start) + ', ' +  str(end))
        return str(random.randint(start, end))
    elif type == 'fixed':
        return str(random.choice(singol_arg['values']))
    elif type == 'immutable':
        return singol_arg['immutable_value']
    else:
        raise Exception(type + ' type of value unknown.\n') 


def gen_terminal(cmd_info, elem):
    try:
        arg = cmd_info['arg']
    except:
        arg = []
    return generate_value(cmd_info[elem]) if elem in arg else str(cmd_info[elem])


# NOT USED
# build at command to send a message to a specific phone number with a random string message
def gen_message_command(cmd_gram):
    first, second = 'AT', ''
    flag = True
    for e in cmd_gram['struct']:
        if e == 'enter':
            cmd = '\r\n'
        elif e == 'ctrl_z':
            cmd = '\x1A'
        else:
            cmd = '"'+gen_terminal(cmd_gram, e)+'"' if e == 'phone_number' else gen_terminal(cmd_gram, e)
        
        if flag:
            first += cmd
        else: 
            second += cmd
        
        if e == 'enter':
            flag = False
    return [first, second]


# build one at command based on the grammar structure 'gram_struct' in input and the command info in 'cmd_info'
# if the command name is 'CMGS' it will build a specific command for the message
def gen_command(cmd_gram):
    if cmd_gram['cmd'] == '+CMGS':
        return gen_message_command(cmd_gram)
    else:
        gram_struct = cmd_gram['struct']
        cmd = ''
        previous_was_arg = 0
        for elem in gram_struct:
            term = gen_terminal(cmd_gram, elem)
            try:
                arg = cmd_gram['arg']
            except:
                arg = []
            if elem in arg:
                if term != 'null':
                    cmd += (cmd_gram['separator'] + term) if len(arg) > 1 and previous_was_arg == 1 else term
                    previous_was_arg = 1
            else:
                cmd += term
                previous_was_arg = 0
    return cmd


if __name__ == '__main__':
    import json
    conf = json.load(open('commandGrammar.json'))
    grammars = conf['AT_CMD_GRAMMARS']
    #print len(grammars.keys())
    # grammars : I, D, +CMUX, +CMGS, +CRLP, +COPS, +CCFC, +CTFR, +CPBS, +CPBR, +CPBW, +CRSM, +CGDCONT, +CGEQMIN
    sample = random.sample(grammars.keys(), 20)
    gram_list = []
    for i in sample:
        print(i)
        gram = grammars[i]
        cmd = gen_command(gram)
        gram_list.append(str(cmd))
    for e in gram_list:
        print(e)
