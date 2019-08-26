
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

        s = '\n --- Select which type of fuzz you want to execute ---\n' \
            ' > 0 - Standard fuzz (includes crossover, mutation, feedback evaluation)\n' \
            ' > 1 - No feedback fuzz\n' \
            ' > 2 - No crossover fuzz\n' \
            ' > 3 - No mutation fuzz\n'
        fuzz_type = int(input(s))

        if input_grams == 'multi':
            multiGrammarFuzzer.main(input_device, fuzz_type, input_port)
        else:
            grammarFuzzer.main(input_grams, input_device, fuzz_type, input_port)


if __name__ == '__main__':
    main()
