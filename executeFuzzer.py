#!/usr/bin/env python2

'''
    file name:      executeFuzzer.py
    authors:        Imtiaz Karim (karim7@purdue.edu), Fabrizio Cicala (fcicala@purdue.edu)
    python version: python 2.7.15
'''

import sys
import multiGrammarFuzzer
import grammarFuzzer


def check_blu_addr(address):
    if address is None:
        print (' Error: Incorrect Bluetooth MAC address. The given address is None.\n')
        return False
    adrs_bytes = address.split(':')
    allow_char = ['0', '1', '2', '3', '4', '5', '6', '7' ,'8', '9', 'a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F'] 
    if len(adrs_bytes) != 6:
        print (' Error: Incorrect Bluetooth MAC address. The given address is too short.\n')
        return False
    for b in adrs_bytes:
        if len(b) != 2:
            print (' Error: Incorrect Bluetooth MAC address. The given address contains invalid fields.\n')
            return False
        if b[0] not in allow_char or b[1] not in allow_char:
            print (' Error: Incorrect Bluetooth MAC address. The given address contains invalid characters.\n')
            return False
    return True


def check_fuzz_settings(settings):
    options = settings.split(',')
    if len(options) > 8:
        print (' Error: Too many options, the number of options must be 8! Try again!\n')
        return False
    if len(options) < 8:
        print (' Error: Options missing, the number of options must be 8! Try again!\n')
        return False
    index = 0
    for s in options:
        index += 1
        if s != '0' and s != '1':
            print (' Error: Invalid option in position ' + str(index) +  '. Try again!\n')
            return False
    return True


usage_message = 'Usage: ./grammarFuzzer.py\
    <grammar1,grammar2,...,grammarN> OR "multi"\
    <device_name>   <port (optional)>\n\
    note: with "multi" option the fuzzer will use line with multiple random commands as input\n'
def main():
    if len(sys.argv) < 3:
        print ('Error: missing argument')
        print (usage_message)
        sys.exit()
    elif len(sys.argv) > 4:
        print ('Error: too many arguments')
        print (usage_message)
        sys.exit()
    else:
        input_grams = sys.argv[1]
        input_device = sys.argv[2]
        input_port = sys.argv[3] if len(sys.argv) == 4 else None

        s = '\n --- Select which type of fuzzer you want to execute ---\n' \
            ' You can completely customize you fuzzer by chosing the fuzzing options.\n' \
            ' There are 8 options:\n' \
            ' feedback, crossover, field addition, field trimming, condition negation, type negation, fixed integers, connectors alteration\n' \
            ' Enter a list of 1/0, separated by comma, to specify whether you want an options or not (1 = yes, 0 = not)\n' \
            ' Example: 1,1,0,0,1,0,1,0\n\n'

        fuzz_settings = raw_input(s) 
        while (not check_fuzz_settings(fuzz_settings)):
            fuzz_settings = raw_input(s)

        s = '\n --- Select which channel you want to use for fuzzing ---\n' \
            ' > b - Bluetooth\n' \
            ' > u - USB\n' \
            ' > t - Test execution (does not require any connected device)\n\n'

        fuzzer_channel = raw_input(s)
        while (fuzzer_channel not in ['b' , 'u', 't']):
            print ('\nOption not valid, try again!')
            fuzzer_channel = raw_input(s)

        blu_addr = None
        if fuzzer_channel == 'b':
            blu_addr = str(raw_input('\n You have selected Bluetooth fuzzer.\n' \
                        ' Please insert the Bluetooth MAC address of the target device. ' \
                        '(Use the format XX:XX:XX:XX:XX:XX)\n'))
            while (check_blu_addr(blu_addr) is False):
                blu_addr = str(raw_input(' Please insert the Bluetooth MAC address of the target device. ' \
                        '(Use the format XX:XX:XX:XX:XX:XX)\n'))

        print ('\n --- Executing ATFuzzer! ---\n')

        if input_grams == 'multi':
            #print ('multi', fuzzer_channel, input_device, fuzz_settings, blu_addr, input_port)
            multiGrammarFuzzer.main(fuzzer_channel, [], input_device, fuzz_settings, blu_addr, input_port)
        else:
            input_grams = input_grams.split(',')
            if len(input_grams) > 1:
                #print ('many', fuzzer_channel, input_grams, input_device, fuzz_settings, blu_addr, input_port)
                multiGrammarFuzzer.main(fuzzer_channel, input_grams, input_device, fuzz_settings, blu_addr, input_port)
            else:
                #print ('single', fuzzer_channel, input_grams[0], input_device, fuzz_settings, blu_addr, input_port)
                grammarFuzzer.main(fuzzer_channel, input_grams[0], input_device, fuzz_settings, blu_addr, input_port)


def test():
    MAX_INT = int(float('inf'))
    MIN_INT = int(float('-inf'))

    print (MAX_INT)
    print (MIN_INT)

if __name__ == '__main__':
    main()
    #test()
   