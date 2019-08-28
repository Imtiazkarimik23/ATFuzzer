
import sys
import multiGrammarFuzzer
import grammarFuzzer


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
            ' > t - Test execution (does not require any connected device)'

        fuzzer_channel = raw_input(s)
        while (fuzzer_channel not in ['b' , 'u', 't']):
            print '\nOption not valid, try again!'
            fuzzer_channel = raw_input(s)


        if input_grams == 'multi':
            multiGrammarFuzzer.main(fuzzer_channel, input_device, fuzz_type, input_port)
        else:
            grammarFuzzer.main(fuzzer_channel, input_grams, input_device, fuzz_type, input_port)


if __name__ == '__main__':
    main()
