# ATFuzzer


"Opening Pandora's Box through ATFuzzer: Dynamic Analysis of AT Interface for Android Smartphones" is accepted to the 35th Annual Computer Security Applications Conference (ACSAC) 2019.
https://relentless-warrior.github.io/wp-content/uploads/2019/11/atfuzz.pdf

# Abstract
This paper focuses on checking the correctness and robustness of
the AT command interface exposed by the cellular baseband processor through Bluetooth and USB. A device’s application processor
uses this interface for issuing high-level commands (or, AT commands) to the baseband processor for performing cellular network
operations (e.g., placing a phone call). Vulnerabilities in this interface can be leveraged by malicious Bluetooth peripherals to launch various attacks including DoS and privacy attacks. To identify such vulnerabilities, we propose ATFuzzer that uses a grammar-guided evolutionary fuzzing approach which mutates production rules of the AT command grammar instead of concrete AT commands. Empirical evaluation with ATFuzzer on 8 Android smartphones from 5 vendors revealed 4 invalid AT command grammars over Bluetooth and 13 over USB with implications ranging from DoS, downgrade of cellular protocol version to severe privacy leaks.

# Run ATFuzzer

## Requirements
Python 2.7.15. Please do not use python 3 because there are library incompatibilities. The required libraries are specified in the file *requirements.txt* and they can be installed executing the command:

``` pip install -r requirements.txt ```

**Note**: the module *pybluez* for python 2.7 is not compatible with Windows. To install *pybluez* on Windows it is necessary to download a previous version. Download *PyBluez‑0.22‑cp27* at [pybluez](www.lfd.uci.edu/~gohlke/pythonlibs/#pybluez) and install it with the command:

``` pip install <pybluez file.whl> ```

## How to run
To run ATFuzzer execute the following command:

*sudo python  executeFuzzer.py  \<list\_of\_grammars\>  \<device\_name\>  \<port (optional)\>*

Alternatively, it is possible to execute ATFuzzer with multiple random chosen grammars with the command:

*sudo python executeFuzzer.py multi \<device\_name\> \<port (optional)\>*


The program then asks to choose among 4 option:
 - 0 - Standard fuzzer (includes crossover, mutation, feedback evaluation)
 - 1 - No feedback fuzzer
 - 2 - No crossover fuzzer
 - 3 - No mutation fuzzer


These options allows the user to choose which type of ATFuzzer to run.  This is fundamental to test and evaluate the effectiveness of our fuzzer.

Finally, ATFuzzer requires to specify which channel will be used for the AT commands transmission.  It is possible to select one among three options:
 - b - Bluetooth
 - u - USB
 - t - Test execution (does not require any connected device)

If the Bluetooth option is selected, the program asks for the Bluetooth address of the target device. The user may insert the Bluetooth MAC address of the device in the specific format: XX:XX:XX:XX:XX:XX (e.g., 1A:2B:3C:4D:5E:6F).

Test execution executes ATFuzzer with fake evaluation parameters and without submitting any command to a device. This option is only for testing purpose, so do not use it to fuzz an actual smartphone.

**Note**: if you run Bluetooth ATFuzzer on Linux, it may be necessary to execute the program with *sudo*, depending on the system configuration.


# Structure of ATFuzzer implementation
In the following we provide a description of the structure of the implementation of ATFuzzer.

**commandGrammar.json**: json file which contains a set of grammars for more that 80 AT commands. The grammars are defined following a specific structure that allows the program to efficiently read them.


**executeFuzzer.py**: main program which allows the user to run ATFuzzer. It provides different options of execution (see *How to run*).


**grammarFuzzer.py**: implements the actual fuzzing. It reads the grammars for the AT commands submitted by the user and performs the fuzzing loop: *input generation - input submission - grammar evaluation - grammar evolution*.


**multiGrammarFuzzer.py**: implements the actual fuzzing. It reads the grammars for the randomly chosen AT commands and performs the fuzzing loop: *input generation - input submission - grammar evaluation - grammar evolution*.


**grammarModifier.py**: implements the functions for the evolution phase. Such functions include grammar crossover and grammar mutation.


**inputGen.py**: generates an random AT command instance given a input grammar.


**atCmdInterface.py**: implements the functions necessary to interact with the AT interface of the target device. It is responsible for setting up the communication with the device, submitting the AT command instances, and finally collecting and evaluating the responses.


**afl_fuzzer.py**: implements the functions used to execute AFL fuzzer in the context of AT commands.


**utilityFunctions.py**: implements support functions for the execution of the main program.


**results**: directory containing the results of each ATFuzzer execution.

## Demo
https://www.youtube.com/watch?v=qR4Pq5i0IRE

## Citation
If your research find one or several components of savior useful, please cite the following paper:
```@inproceedings{karim2019opening,
  title={Opening Pandora's box through ATFuzzer: dynamic analysis of AT interface for Android smartphones},
  author={Karim, Imtiaz and Cicala, Fabrizio and Hussain, Syed Rafiul and Chowdhury, Omar and Bertino, Elisa},
  booktitle={Proceedings of the 35th Annual Computer Security Applications Conference},
  pages={529--543},
  year={2019}
} ```
