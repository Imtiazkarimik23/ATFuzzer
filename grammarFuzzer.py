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

standard_grammar = {}           # standard version of the grammar
stored_grammar = []             # list of grammars that triggered an issue
current_population = []         # list of current grammars in the population
current_grammar = {}            # grammar currently fuzzing
cmd_window = deque(maxlen=10)   # queue to keep track of the previous commands


# --- EXECUTION PARAMETERS --- #
ATTEMPTS = 10                   # number of iterations
RESTART_TRESHOLD = 3            # number of repetetion of all the iteration
INPUT_NUMBER = 5                # number of input generated for each grammar


def read_conf():
    conf = json.load(open('commandGrammar.json'))
    return conf['AT_CMD_GRAMMARS']


def save_current_state():
    data = {
        'current_set': current_population,
        'current_grammar': current_grammar,
        'stored_grammar': stored_grammar
    }
    with open(log_file, 'w') as f:
        json.dump(data, f)


def update_current(gram):
    global current_grammar
    current_grammar = gram


# Method that starting from a set of grammars for the generation of an AT command generates
# a specific number of different versions of each grammar through the execution of 3 steps:
#   1. random crossovering of elements in the given grammar
#   2. random modification of the given grammar by adding or deleting one element
#   3. random modification of the given grammar to make it generate invalid commands
# # input: 
#       grammars = list of grammars that can generate a specific AT command
#       diversification_factory = number of new grammar to generate for each given grammar
# # output: mutated_grams = list of new modified grammars
def create_population(grammars, diversification_factor=1):
    mutated_grams = []
    for g in grammars:
        cmd_gram = utilityFunctions.copy_dict(g)
        update_current(cmd_gram)
        generated = 0
        while generated < diversification_factor:
            ''' 
            global move_command
            if move_command == 0:
                move_command = 1 if utilityFunctions.flip_coin(10) == 1 else 0
            '''

            # 3 steps:
            # 1. random crossover
            # check if no crossover fuzzer
            new_gram = utilityFunctions.copy_dict(gram_crossover(cmd_gram, move_command)) if fuzz_type != 2 else utilityFunctions.copy_dict(cmd_gram)

            if fuzz_type != 3:  # check if no mutation fuzz
                # 2. random add or delete
                if utilityFunctions.flip_coin() == 1:
                    gram_random_add_delete(new_gram, move_command)
                
                # 3. random valid/invalid
                if utilityFunctions.flip_coin() == 1:
                    make_gram_invalid(new_gram)
                
            if new_gram not in stored_grammar and new_gram != standard_grammar:
                mutated_grams.append(new_gram)
                generated += 1
    return mutated_grams


hyperparameters = {
    'time_weight': 0.6,
    'flag_weight': 0.4,
    'curr_score_weight': 0.7,
    'prev_score_weight': 0.3
}
def select_population(scores):
    selected_grammars = []
    if fuzz_type == 1:  # no feedback fuzz
        for scr in scores:
            selected_grammars.append(scores[scr]['grammar'])
        # randomly select 5 grammars
        return random.sample(selected_grammars, 5)
    else:
        for scr in scores:
            gram = scores[scr]['grammar']
            time, flag = scores[scr]['score'][0], scores[scr]['score'][1]
            score = hyperparameters['time_weight'] * time + hyperparameters['flag_weight'] * flag
            previous_score = gram['score']
            new_score = (hyperparameters['curr_score_weight']*score + hyperparameters['prev_score_weight']*previous_score) if previous_score != 0 else score    
            # it takes into cosideration the score of the previous iteration
            gram['score'] = new_score 
            utilityFunctions.gram_sorted_insert(selected_grammars, gram)
            
        # select the first 5 grammars
        return selected_grammars[:5]


def evaluate_command(cmd):
    if fuzz_channel == 'b':
        return bluetooth_fuzz(cmd, port)
    elif fuzz_channel == 'u':
        return usb_fuzz(cmd, device, port)
    elif fuzz_channel == 't': # only for test purpose
        print(cmd)
        return test_fuzz(cmd)
    else:
        print('\nInvalid fuzzer channel! Restart execution and follow the instructions\n')
        sys.exit()
    


def save_grammar(gram, cmd):
    if gram not in stored_grammar:
        stored_grammar.append(gram)
    s = utilityFunctions.build_string_gram_cmd(gram, cmd)
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


def evaluate_grammar(cmd_gramm):
    timing = []
    flag = 0
    for _ in range(INPUT_NUMBER):
        cmd = 'AT' + inputGen.gen_command(cmd_gramm)
        cmd_window.append(cmd)
        result = evaluate_command(cmd, cmd_gramm['cmgf_flag']) if cmd_gramm['cmd'] == '+CMGS' else evaluate_command(cmd)
        timing.append(result[0])
        if result[1] == 1:
            save_grammar(cmd_gramm, cmd)
            flag = 1
    return [utilityFunctions.average(timing), flag]


def preprocess_gram_set_up(gram):
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


def evaluate_grammars(input_grams):
    gram_to_fuzz = input_grams.split(',')

    grammars = read_conf()
    for gram in gram_to_fuzz:
        try:
            test_cmd_gram = grammars[gram]
        except:
            raise Exception('Error: unknown grammar')

        preprocess_gram_set_up(test_cmd_gram)
        global standard_grammar
        if len(test_cmd_gram['struct']) > 3:
            standard_grammar = test_cmd_gram
        else:
            global move_command
            move_command = 1

        for count in range(RESTART_TRESHOLD):
            gram_population = create_population([test_cmd_gram], 10)

            grammar_scores = {}
            for i in range(ATTEMPTS):
                print('Attempt counter: ', i)
                global current_population
                current_population = gram_population
                j = 0
                for gram in gram_population:
                    update_current(gram)
                    grammar_scores[j] = {}
                    grammar_scores[j]['grammar'] = gram
                    grammar_scores[j]['score'] = evaluate_grammar(gram)
                    j += 1

                selected_gram = select_population(grammar_scores)
                gram_population = create_population(selected_gram, 2)
            print('Execution restart counter: ', count)
            print('__________________________________________________\n')


def main(channel, input_grams, input_device, type_of_fuzz, input_port):
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
        evaluate_grammars(input_grams)
        print('\nExecution time: ', (time.time() - start_time))
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        save_current_state()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print('Current grammar: ', current_grammar)
        print('\nExecution time: ', (time.time() - start_time))
        sys.exit()


if __name__ == '__main__':
    main('test', 'ATD', 'test_dev', 0, None)

