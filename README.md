# ATFuzzer
"Opening Pandora's Box through ATFuzzer: Dynamic Analysis of AT Interface for Android Smartphones" is accepted to the 35th Annual Computer Security Applications Conference (ACSAC) 2019.

# Abstract: 
This paper focuses on checking the correctness and robustness of
the AT command interface exposed by the cellular baseband processor through Bluetooth and USB. A device’s application processor
uses this interface for issuing high-level commands (or, AT commands) to the baseband processor for performing cellular network
operations (e.g., placing a phone call). Vulnerabilities in this interface can be leveraged by malicious Bluetooth peripherals to launch various attacks including DoS and privacy attacks. To identify such vulnerabilities, we propose ATFuzzer that uses a grammar-guided evolutionary fuzzing approach which mutates production rules of the AT command grammar instead of concrete AT commands. Empirical evaluation with ATFuzzer on 8 Android smartphones from 5 vendors revealed 4 invalid AT command grammars over Bluetooth and 13 over USB with implications ranging from DoS, downgrade of cellular protocol version to severe privacy leaks.

# How to run:
To run ATFuzzer execute the following command:

*python  executeFuzzer.py  \<list\_of\_grammars\>  \<device\_name\>  \<port (optional)\>*

Alternatively, it is possible to execute ATFuzzer with multiple random chosen grammars with the command:

*python executeFuzzer.py multi \<device\_name\> \<port (optional)\>*
 

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
