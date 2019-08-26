
#!/usr/bin/env python2

import sys
import json
import random
import string
import traceback
import inputGen
import utility
import time
from numpy import setdiff1d
from atsend import fuzz, fuzz_message, fuzz_blue


log_file = 'log/grammarFuzzer_log.json'

# Global variables
fuzz_type = 0
move_command = 1
device = 'unknown'
port = None
standard_grammar = {}
stored_grammar = []
current_set = []
current_grammar = {}

def read_conf():
    conf = json.load(open('commandGrammar.json'))
    return conf['AT_CMD_GRAMMARS']


def save_current_state():
    data = {
        'current_set': current_set,
        'current_grammar': current_grammar,
        'stored_grammar': stored_grammar
    }
    with open(log_file, 'w') as f:
        json.dump(data, f)


def update_current(gram):
    global current_grammar
    current_grammar = gram


def gram_crossover(cmd_gram):
    gram_struct = cmd_gram['struct']
    if len(gram_struct) > 2:
        start = 0 if move_command == 1 else 2
        i, j = random.randint(start, len(gram_struct)-1), random.randint(start, len(gram_struct)-1)
        gram_struct[i], gram_struct[j] = gram_struct[j], gram_struct[i]
    return cmd_gram


def add_field(cmd_gram):
    gram_struct = cmd_gram['struct']
    possible_elements = utility.remove_elements(cmd_gram.keys(), ['struct', 'arg', 'separator', 'score'])
    missing_elements = setdiff1d(possible_elements, gram_struct)
    if len(missing_elements) > 0:
        gram_struct.append(random.choice(missing_elements))


def remove_field(cmd_gram):
    gram_struct = cmd_gram['struct']
    if len(gram_struct) > 2:
        start = 0 if move_command == 1 else 2
        gram_struct.pop(random.randint(start, len(gram_struct)-1))


# Method that takes as input a list of elements and add/delete an element to/from that list
# # input: cmd_gram = detailed grammar dictionary
def gram_random_add_delete(cmd_gram):
    gram_struct = cmd_gram['struct']
    if len(gram_struct) < 2 or utility.flip_coin() == 0:
        add_field(cmd_gram)
    else:
        remove_field(cmd_gram)


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
            if utility.flip_coin(2) > 0:
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
            arg['range'] = random.choice([[end+1, end+100], [start-100, start-1]])

        elif type == 'fixed':
            if utility.flip_coin() == 0:
                new_value = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(10))
                arg['values'].append(new_value)
            else:
                cmd_gram[arg_name] = { "type": "string", "length": 10 }
        
        elif type == 'immutable':
            pass
        else:
            raise Exception("Error: unknow argument type")


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
        cmd_gram = utility.copy_dict(g)
        update_current(cmd_gram)
        generated = 0
        while generated < diversification_factor:
            ''' 
            global move_command
            if move_command == 0:
                move_command = 1 if utility.flip_coin(10) == 1 else 0
            '''

            # 3 steps:
            # 1. random crossover
            # check id no crossover fuzzer
            new_gram = utility.copy_dict(gram_crossover(cmd_gram)) if fuzz_type != 2 else utility.copy_dict(cmd_gram)

            if fuzz_type != 3:  # check if no mutation fuzz
                # 2. random add or delete
                if utility.flip_coin() == 1:
                    gram_random_add_delete(new_gram)
                
                # 3. random valid/invalid
                if utility.flip_coin() == 1:
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
    ''' 
    total_time = 0
    for scr in scores:
        total_time += scores[scr]['score'][0]
    '''
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
            utility.sorted_insert(selected_grammars, gram)
            
        # select the first 5 grammars
        return selected_grammars[:5]



def evaluate_command(cmd, sms_flag=None):
    return fuzz_blue(cmd) if sms_flag is None else fuzz_message(cmd, device, sms_flag, port)


def save_grammar(gram, cmd):
    if gram not in stored_grammar:
        stored_grammar.append(gram)
    s = utility.build_string_gram_cmd(gram, cmd)
    if fuzz_type == 0:
        fuzz_type_name = '_standard'
    elif fuzz_type == 1:
        fuzz_type_name = '_noFeedback'
    elif fuzz_type == 2:
        fuzz_type_name = '_noCrossover'
    elif fuzz_type == 3:
        fuzz_type_name = '_noMutation'
    with open('results/grammar_fuzzing_result_' + device + fuzz_type_name + '.txt', 'a') as f:
        f.write(s)


INPUT_NUMBER = 5
def evaluate_grammar(cmd_gramm):
    timing = []
    flag = 0
    for _ in range(INPUT_NUMBER):
        cmd = inputGen.gen_command(cmd_gramm)
        print cmd
        result = evaluate_command(cmd, cmd_gramm['cmgf_flag']) if cmd_gramm['cmd'] == '+CMGS' else evaluate_command(cmd)
        #result = [random.random()*5, 0] 
        timing.append(result[0])
        if result[1] == 1:
            save_grammar(cmd_gramm, cmd)
            flag = 1
    return [utility.average(timing), flag]


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


# ATTEMPTS = 10, RESTART_TRESHOLD = 4 ==> 3.5 hours of execution for each grammar (3 sec per command)
# ATTEMPTS = 18, RESTART_TRESHOLD = 5 ==> 8 hours of execution for each grammar (3 sec per command)
# ATTEMPTS = 50, RESTART_TRESHOLD = 10 ==> 40 hours of execution for each grammar (3 sec per command)
ATTEMPTS = 10
RESTART_TRESHOLD = 3
def evaluate_grammars():
    gram_to_fuzz = sys.argv[1].split(',')
    global device
    device = sys.argv[2]
    if len(sys.argv) == 4:
        global port
        port = sys.argv[3]

    grammars = read_conf()
    for gram in gram_to_fuzz:
        try:
            test_cmd_gram = grammars[gram]
        except:
            raise Exception('Error: unknown grammar')

        preprocess_gram_set_up(test_cmd_gram)
        global standard_grammar
        if len(test_cmd_gram['struct']) > 3 and test_cmd_gram['cmd'] != '+CMGS':
            standard_grammar = test_cmd_gram
        
        global move_command
        if len(test_cmd_gram['struct']) < 3 and test_cmd_gram['cmd'] != '+CMGS':
            move_command = 1

        for count in range(RESTART_TRESHOLD):
            gram_population = create_population([test_cmd_gram], 10)

            grammar_scores = {}
            for i in range(ATTEMPTS):
                print 'Attempt counter: ', i
                global current_set
                current_set = gram_population
                j = 0
                for gram in gram_population:
                    update_current(gram)
                    grammar_scores[j] = {}
                    grammar_scores[j]['grammar'] = gram
                    grammar_scores[j]['score'] = evaluate_grammar(gram)
                    j += 1

                selected_gram = select_population(grammar_scores)
                gram_population = create_population(selected_gram, 2)
            print 'Execution restart counter: ', count
            print '__________________________________________________\n'
            

usage_message = 'Usage: ./grammarFuzzer.py <grammar1,grammar2,...,grammarN> <device_name> <port (optional)>'
def main():
    if len(sys.argv) < 3:
        print 'Error: missing argument'
        print usage_message
        sys.exit()
    elif len(sys.argv) > 4:
        print 'Error: too many arguments'
        print usage_message
        sys.exit()
    else:
        global fuzz_type
        s = '\n --- Select which type of fuzz you want to execute ---\n' \
            ' > 0 - Standard fuzz (includes crossover, mutation, feedback evaluation)\n' \
            ' > 1 - No feedback fuzz\n' \
            ' > 2 - No crossover fuzz\n' \
            ' > 3 - No mutation fuzz\n'
        fuzz_type = int(input(s))

        start_time = time.time()
        try:
            evaluate_grammars()
            print '\nExecution time: ', (time.time() - start_time)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            save_current_state()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print 'Current grammar: ', current_grammar
            print '\nExecution time: ', (time.time() - start_time)
            sys.exit()


def test():
    grammars = read_conf()
    print len(grammars.keys())


if __name__ == '__main__':
    main()
    #test()