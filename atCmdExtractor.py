#!/usr/bin/env python3


import PyPDF2
import re
import camelot
import sys


file_3gpp = 'ATCmd_manuals/3GPP.pdf'
file_gtm = 'ATCmd_manuals/gtm-203m-3gwa_atcommands_manual.pdf'
file_sim9000 = 'ATCmd_manuals/SIM900_AT Command Manual_V1.11.pdf'
file_telit = 'ATCmd_manuals/Telit_AT_Commands_Reference_Guide_r24_B.pdf'


# Possible formats: 
# AT<cmd>, AT<symbol><cmd>
# ATCMD?
# ATCMD=?
# ATCMD<par>[,<par>[,par>]][,<par>]     - ex. ATD<n>[<mgsm>][;]
# ATCMD=<par>[,<par>[,<par>]][,<par>]   - ex. AT+CAMM=<acmmax>[,<passwd>], AT+CBST=<speed>[,<name>[,<ce>]]
# ATCMD=[<par>[,<par>[,<par>]]][,<par>] - ex.          
# #
regex = '(?P<cmd>AT[!@#$%^&*+]?[A-Z\d]+)(?P<arg>(\?|=\?|(=|\s|\[[<>\["+:;%,?\s\w\d]+\]+|[<>]+[;\s\w\d]+>|,))*)'


def replaceMultiple(mainString, toBeReplaces, newString):
    for elem in toBeReplaces:
        if elem in mainString:
            mainString = mainString.replace(elem, newString)
    return  mainString


def clean_cmd(cmd):
    cmd = replaceMultiple(str(cmd), [' ', '[', ']', '\n'] , '')
    if cmd[-1:] == ',':
        cmd = cmd[:-1]
    if cmd[-1:] == '?':
        cmd = cmd[:-1]
    if cmd[-1:] == '=':
        cmd = cmd[:-1]
    if cmd[:2] == 'AT':
        cmd = cmd[2:]
    return cmd


def at_cmd_extractor(input_file, tables_flag):
    print ('Analyzing ' + input_file + '\n')   
    commands = []

    if tables_flag == '1':
        tables = camelot.read_pdf(input_file, pages = '1-end')
        for t in tables:
            if input_file == file_3gpp:           
                if str(t.df[0][0]) == 'Command':
                    cmd = clean_cmd(t.df[0][1])
                    if cmd != '' and cmd not in commands:
                        commands.append(cmd)
            #input_file == file_telit
            else:
                for i in range(1, len(t.df[0])):
                    cmd = str(t.df[0][i])    
                    if cmd[:2] == 'AT':
                        cmd = clean_cmd(cmd)
                        if cmd != '' and cmd not in commands:
                            commands.append(cmd)

    elif tables_flag == '0':
        read_pdf = PyPDF2.PdfFileReader(input_file)
        NumPages = read_pdf.getNumPages()  
        for i in range(1, NumPages):
            page = read_pdf.getPage(i)
            page_content = page.extractText()
            in_line_page_content = page_content.replace('\n', ' ')
            #print (in_line_page_content)
            cmds = re.findall(regex, in_line_page_content)
            for tup in cmds:
                #print (tup)
                if tup[1] != '?' and tup[1] != '=?':
                    cmd = tup[0] + tup[1]
                    cmd = clean_cmd(cmd)
                    if cmd != '' and cmd not in commands:
                        commands.append(cmd)
    else:
        print ('Error: Non valid argument.\n')
        exit()                
    
    commands.sort()
    output = input_file + '_extracted_ATCmd'
    with open(output, 'w') as f:
        for cmd in commands:
            if cmd != '':
                f.write(cmd+'\n')
    





usage_message = 'Usage: ./atCmdExtractor.py \t <file.pdf> \t <commads_in_tables_flag>\n'

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ('Error: missing argument')
        print (usage_message)
        sys.exit()
    elif len(sys.argv) > 3:
        print ('Error: too many arguments')
        print (usage_message)
        sys.exit()
    else:
        input_file = sys.argv[1]
        tables_flag = sys.argv[2]
    '''
    input_file = file_telit
    tables_flag = 0
    '''
    print ('--- AT Commands Extractor ---\n')
    at_cmd_extractor(input_file, tables_flag)
    print ('--- Execution Terminated ---\n')
    