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
        return False
    bytes = address.split(':')
    allow_char = ['0', '1', '2', '3', '4', '5', '6', '7' ,'8', '9', 'A', 'B', 'C', 'D', 'F'] 
    if len(bytes) != 6:
        return False
    for b in bytes:
        if len(b) != 2:
            return False
        if b[0] not in allow_char or b[1] not in allow_char:
            return False
    return True


usage_message = 'Usage: ./grammarFuzzer.py\
    <grammar1,grammar2,...,grammarN> OR "multi"\
    <device_name>   <port (optional)>\n\
    note: with "multi" option the fuzzer will use line with multiple random commands as input'
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
        input_grams = sys.argv[1]
        input_device = sys.argv[2]
        input_port = sys.argv[3] if len(sys.argv) == 4 else None

        s = '\n --- Select which type of fuzzer you want to execute ---\n' \
            ' > 0 - Standard fuzzer (includes crossover, mutation, feedback evaluation)\n' \
            ' > 1 - No feedback fuzzer\n' \
            ' > 2 - No crossover fuzzer\n' \
            ' > 3 - No mutation fuzzer\n'

        fuzz_type = int(input(s))
        while (fuzz_type not in [0, 1, 2, 3]):
            print '\nOption not valid, try again!'
            fuzz_type = int(input(s))

        s = '\n --- Select which channel you want to use for fuzzing ---\n' \
            ' > b - Bluetooth\n' \
            ' > u - USB\n' \
            ' > t - Test execution (does not require any connected device)\n'

        fuzzer_channel = raw_input(s)
        while (fuzzer_channel not in ['b' , 'u', 't']):
            print '\nOption not valid, try again!'
            fuzzer_channel = raw_input(s)

        blu_addr = None
        if fuzzer_channel == 'b':
            blu_addr = str(input('\nYou have selected Bluetooth fuzzer.\n' \
                        'Please insert the Bluetooth MAC address of the target device. (Use capital letters)\n'))
            while (check_blu_addr(blu_addr) is False):
                blu_addr = str(input('\nThe inserted address is incorrect!\n' \
                        'Please insert the Bluetooth MAC address of the target device. (Use capital letters)\n'))

        if input_grams == 'multi':
            multiGrammarFuzzer.main(fuzzer_channel, input_device, fuzz_type, blu_addr, input_port)
        else:
            grammarFuzzer.main(fuzzer_channel, input_grams, input_device, fuzz_type, blu_addr, input_port)


if __name__ == '__main__':
    main()
