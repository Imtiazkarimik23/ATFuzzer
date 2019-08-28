#!/usr/bin/env python2.7

import sys
import json
import random
import string
import traceback
import inputGen
import utilityFunctions
import time
from atCmdInterface import usb_fuzz, bluetooth_fuzz, test_fuzz
from collections import deque
from grammarModifier import *
from numpy import setdiff1d


log_file = 'log/grammarFuzzer_log.json'

# Global variables
fuzz_channel = 'unknown'        # it may be USB or Bluetooth                   
fuzz_type = 0                   # fuzzing type: standard, w/o feedback, w/o crossover, w/o mutation 
move_command = 0                # during the mutation with 0 the position of the command is fixed; with 1 it is variable
device = 'unknown'              # device name (e.g. Nexus6P)
port = None

current_population = []         # list of current grammars/grammars sets in the population
cmd_window = deque(maxlen=10)   # queue to keep track of the previous commands
current_set = []                # list of multiple grammars currently fuzzing
standard_set = []               # list of standard versions of the grammars
stored_set = []                 # list of sets of grammars that triggered an issue


# --- EXECUTION PARAMETERS --- #
ATTEMPTS = 10                   # number of iterations
RESTART_TRESHOLD = 3            # number of repetetions of all the iterations
INPUT_NUMBER = 5                # number of input generated for each grammar
CMD_NUMBER = 3                  # number of commands in the input line


def read_conf():
    conf = json.load(open('commandGrammar.json'))
    return conf['AT_CMD_GRAMMARS']


def save_current_state():
    data = {
        'current_population': current_population,
        'current_set': current_set,
        'stored_set': stored_set
    }
    with open(log_file, 'w') as f:
        json.dump(data, f)


def update_current(gram_set):
    global current_set
    current_set = gram_set


def save_set(gram_set):
    if gram_set not in stored_set:
        stored_set.append(gram_set)
    s = utilityFunctions.build_string_set_gram_cmd(gram_set, cmd_window)
    if fuzz_type == 0:
        fuzz_type_name = '_standard'
    elif fuzz_type == 1:
        fuzz_type_name = '_noFeedback'
    elif fuzz_type == 2:
        fuzz_type_name = '_noCrossover'
    elif fuzz_type == 3:
        fuzz_type_name = '_noMutation'
    with open('results/' + device + fuzz_type_name + '.txt', 'a') as f:
        f.write(s)


# Method that one grammar for the generation of an AT command as input and generates
# one different versiont of the grammar through the execution of 3 steps:
#   1. random crossovering of elements in the given grammar
#   2. random modification of the given grammar by adding or deleting one element
#   3. random modification of the given grammar to make it generate invalid commands
def modify_grammar(gram):
    cmd_gram = utilityFunctions.copy_dict(gram)
    ''' 
    global move_command
    if move_command == 0:
        move_command = 1 if utilityFunctions.flip_coin(10) == 1 else 0
    '''
    # 3 steps:
    # 1. random crossover
    # check if no crossover fuzzer
    new_gram = utilityFunctions.copy_dict(gram_crossover(cmd_gram, move_command)) if fuzz_type != 2 else utilityFunctions.copy_dict(
        cmd_gram)

    if fuzz_type != 3:  # check if no mutation fuzz
        # 2. random add or delete
        if utilityFunctions.flip_coin() == 1:
            gram_random_add_delete(new_gram, move_command)

        # 3. random valid/invalid
        if utilityFunctions.flip_coin() == 1:
            make_gram_invalid(new_gram)

    return new_gram


# method that accepts a list of grammars as input and returns a list of as new list as the diversification factor
## input:
#   gram_set = list of grammars of one set
#   diversification_factor = define how many new sets to generate from the input one
## output: midified_set = list of sets of grammars
## example:
#   input = set1, diversification_factor=2
#   output = [set1', set1'']
def modify_set(gram_set, diversification_factor):
    modified_set = []
    for _ in range(diversification_factor):
        modified_set.append([])

    for g in gram_set:
        generated = 0
        previous_gram = {}
        while generated < diversification_factor:
            new_gram = modify_grammar(g)
            if new_gram not in standard_set and new_gram != previous_gram:
                modified_set[generated].append(new_gram)
                generated += 1
                previous_gram = utilityFunctions.copy_dict(new_gram)

    return modified_set


# 
## input:
#   gram_sets: list of list (sequences) of grammars to originate new setes from
#   diversification_factor =  define how many new sets to generate from the each one
## output: new_population = new list of list of grammars
def create_population(gram_sets, diversification_factor=1):
    new_population = []
    for single_set in gram_sets:
        for new_set in modify_set(single_set, diversification_factor):
            new_population.append(new_set)
    return new_population


def evaluate_command(cmd, sms_flag=None):
    if fuzz_channel == 'b':
        return bluetooth_fuzz(cmd)
    elif fuzz_channel == 'u':
        return usb_fuzz(cmd, device, port)
    elif fuzz_channel == 't': # only for test purpose
        print(cmd)
        return test_fuzz(cmd)
    else:
        print('\nInvalid fuzzer channel! Restart execution and follow the instructions\n')
        sys.exit()


def evaluate_set(gram_set):
    timing = []
    flag = 0
    for _ in range(INPUT_NUMBER):
        input_cmd = 'AT'
        for g in gram_set:
            input_cmd += str(inputGen.gen_command(g)) + ';'
        input_cmd = input_cmd[:-1]
        cmd_window.append(input_cmd)
        result = evaluate_command(input_cmd)
    
        timing.append(result[0])
        if result[1] == 1:
            save_set(gram_set)
            flag = 1
    return [utilityFunctions.average(timing), flag]


def gram_setup(gram):
    gram['score'] = 0 
    try:
        gram['arg']
    except:     # no argument is expected
        gram['struct'].append('random')
        gram['arg'] = ['random']
        gram['separator'] = ''
        gram['random'] = {
            "type": "string",
            "length": 5
        }


hyperparameters = {
    'time_weight': 0.6,
    'flag_weight': 0.4,
    'curr_score_weight': 0.7,
    'prev_score_weight': 0.3
}
def select_population(scores):
    set_and_scores = []
    selected_sets = []

    if fuzz_type == 1:  # no feedback fuzz
        for scr in scores:
            selected_sets.append(scores[scr]['set'])
        # randomly select 2 grammars
        return random.sample(selected_sets, 2)
    else:
        for scr in scores:
            set_score = scores[scr]
            reply_time = set_score['score'][0]
            flag = set_score['score'][1]
            score = hyperparameters['time_weight'] * reply_time + hyperparameters['flag_weight'] * flag
            # to add: previous_score
            #if previous_score != 0: (hyperparameters['curr_score_weight'] * score + hyperparameters['prev_score_weight'] * previous_score)
            # it takes into consideration the score of the previous iteration
            set_score['score'] = score
            utilityFunctions.set_sorted_insert(set_and_scores, set_score)

        for set_score in set_and_scores:
            selected_sets.append(set_score['set'])
        # select the first 2 grammars
        return selected_sets[:5]


def fuzz_multi_grams():
    for g in current_set:
        gram_setup(g)
        if len(g['struct']) > 3 and g['cmd'] != '+CMGS':
            standard_set.append(g)

    for count in range(RESTART_TRESHOLD):
        set_population = create_population([current_set], 10)
        set_scores = {}

        for _ in range(ATTEMPTS):
            global current_population
            current_population = set_population
            j=0
            for gram_set in set_population:
                #utilityFunctions.print_grammars_in_set(gram_set)
                update_current(gram_set)
                set_scores[j] = {}
                set_scores[j]['set'] = gram_set
                set_scores[j]['score'] = evaluate_set(gram_set)
                j += 1
                print('\n')

            selected_sets = select_population(set_scores)
            set_population = create_population(selected_sets, 2)

        print('Execution restart counter: ', count+1)
        print('__________________________________________________\n')


def evaluate_grammars():
    grammars = read_conf()
    random_grammars = random.sample(grammars.keys(), CMD_NUMBER)
    print('Fuzzing grammars: ', str(random_grammars))
    for g in random_grammars:
        current_set.append(grammars[g])
    fuzz_multi_grams()


def main(channel, input_device, type_of_fuzz, input_port):
    global fuzz_channel
    fuzz_channel = channel
    global device
    device = input_device
    global fuzz_type
    fuzz_type = type_of_fuzz
    if input_port is not None:
        global port
        port = input_port

    start_time = time.time()
    try:
        evaluate_grammars()
        print('\nExecution time: ', (time.time() - start_time))
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        save_current_state()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print('Current set: ')
        for g in current_set:
            print(g)
        print('\nExecution time: ', (time.time() - start_time))
        sys.exit()


if __name__ == '__main__':
    main('usb', 'test_dev', 0, None)
