# ATFuzzer
"Opening Pandora's Box through ATFuzzer: Dynamic Analysis of AT Interface for Android Smartphones" is accepted to the 35th Annual Computer Security Applications Conference (ACSAC) 2019.

Abstract: 
This paper focuses on checking the correctness and robustness of
the AT command interface exposed by the cellular baseband processor through Bluetooth and USB. A device’s application processor
uses this interface for issuing high-level commands (or, AT commands) to the baseband processor for performing cellular network
operations (e.g., placing a phone call). Vulnerabilities in this interface can be leveraged by malicious Bluetooth peripherals to launch various attacks including DoS and privacy attacks. To identify such vulnerabilities, we propose ATFuzzer that uses a grammar-guided evolutionary fuzzing approach which mutates production rules of the AT command grammar instead of concrete AT commands. Empirical evaluation with ATFuzzer on 8 Android smartphones from 5 vendors revealed 4 invalid AT command grammars over Bluetooth and 13 over USB with implications ranging from DoS, downgrade of cellular protocol version to severe privacy leaks.


USAGE:

sudo ./grammarFuzzer.py    <grammar1,grammar2,...,grammarN> OR "multi"    <device_name>    <port (optional)>
note: with "multi" option the fuzzer will use line with multiple random commands as input'
