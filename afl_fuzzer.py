#!/usr/bin/env python2

import sys
import bitarray
import utilityFunctions
import random
import re
import time
import traceback
from atCmdInterface import usb_fuzz


def flip_n_bits(bit_line, n):
    if n > len(bit_line):
        raise Exception('flip_n_bits: n too high')
    i = 0 if n == len(bit_line) else random.randint(0, len(bit_line) - (n+1))
    end = i+n
    while i < end:
        bit_line[i] = 0 if bit_line[i] == 1 else 1
        i += 1


# Bit flip
def bit_flip(line, coin=None):
    bit_line = bitarray.bitarray()
    bit_line.frombytes(line)
    if coin is None:
        coin = utilityFunctions.flip_coin(4)
    if coin == 0:
        return line
    
    flip_n_bits(bit_line, coin)
    try:
        return str(bit_line.tobytes().decode('utf-8'))
    except:
        return bit_flip(line, coin)


# Byte flip
def byte_flip(line, l=None):
    if (utilityFunctions.flip_coin(2) == 0 and l is None):
        return line

    bit_line = bitarray.bitarray()
    bit_line.frombytes(line)
    flip_width= [8, 16, 32]
    if l is None:
        l = random.choice(flip_width)
        while l > len(bit_line):
            l = random.choice(flip_width)
    flip_n_bits(bit_line, l)
    try:
        return str(bit_line.tobytes().decode('utf-8'))
    except:
        return byte_flip(line, l-1)


def is_number(char):
    try:
        float(char)
        return True
    except:
        return False


# Known integers
def known_integer(cmd):
    if utilityFunctions.flip_coin(2) == 0:
        return cmd
    MAX_INT = sys.maxint
    MIN_INT = -sys.maxint -1
    values = [-1, 256, 1024, MAX_INT-1, MAX_INT, MIN_INT]
    numbers = re.findall(r'\b\d+\b', cmd)
    if len(numbers) > 0:
        elem = random.choice(numbers)
        cmd = cmd.replace(elem, str(random.choice(values)))
    return cmd


def get_blocks(cmd):
    s = cmd
    blocks = []
    block_size = 1 if len(s)<8 else random.randint(1, len(s)/4)
    while len(s) > block_size:
        blocks.append(s[:4])
        s = s[4:]
    blocks.append(s)
    return blocks


# Block deletion
def block_deletion(cmd):
    if utilityFunctions.flip_coin(2) == 0:
        return cmd
    blocks = get_blocks(cmd)
    blocks.pop(random.randint(0, len(blocks)-1))
    return ''.join(blocks)


# Block duplication via overwrite or insertion
def block_swapping(cmd):
    if utilityFunctions.flip_coin(2) == 0:
        return cmd
    blocks = get_blocks(cmd)
    i, j = random.randint(0, len(blocks)-1), random.randint(0, len(blocks)-1)
    blocks[i], blocks[j] = blocks[j], blocks[i] 
    return ''.join(blocks)


def mutate_cmd(original_cmd):
    #print 'original:\t\t', original_cmd
    cmd = original_cmd
    cmd = bit_flip(cmd)
    #print 'bit_flip:\t\t', cmd
    cmd = byte_flip(cmd)
    #print 'byte_flip:\t\t', cmd
    cmd = known_integer(cmd)
    #print 'known_integer:\t', cmd
    cmd = block_deletion(cmd)
    #print 'block_deletion:\t', cmd
    cmd = block_swapping(cmd)
    #print 'block_swapping:\t', cmd
    return cmd


def update_commands_population(commands, div_factor=1):
    new_commands = utilityFunctions.copy_list(commands)
    for cmd in commands:
        for _ in range(div_factor):
            new_cmd = mutate_cmd(cmd)
            new_commands.append(new_cmd)
    return new_commands

def save_command(cmd, dev):
    with open('results/afl_fuzzing_result_' + dev + '.txt', 'a') as f:
        f.write(cmd)


def sort_by_score(couple):
    return couple[0]


def select_population(results):
    results.sort(key = sort_by_score)
    select = [x[1] for x in results[:20]]
    return select


hyperparameters = {
    'time_weight': 0.6,
    'flag_weight': 0.4,
}    

ATTEMPTS = 10
RESTART_TRESHOLD = 3
def fuzz_command(commands, device):
    for x in range(RESTART_TRESHOLD):
        fuzzing_cmd = utilityFunctions.copy_list(commands)
        commands_population = fuzzing_cmd
        print '\nRestart counter: ', x
        for i in range(ATTEMPTS):
            print '\n - Iteration counter: ', i
            results = []
            for cmd in commands_population:
                #print cmd
                #res = [random.random()*5, 0]
                res = usb_fuzz('AT'+cmd, device)
                time, flag = res[0], res[1]
                cmd_result = hyperparameters['time_weight'] * time + hyperparameters['flag_weight'] * flag
                results.append([cmd_result, cmd])
                if flag == 1:
                    save_command(cmd, device)

            selected_commands = select_population(results)
            commands_population = update_commands_population(selected_commands)
        print '__________________________________________________\n'


usage_message = 'Usage: ./afl_fuzzer.py <device_name>'
def main():
    if len(sys.argv) < 2:
        print 'Error: missing argument'
        print usage_message
        sys.exit()
    elif len(sys.argv) > 2:
        print 'Error: too many arguments'
        print usage_message
        sys.exit()
    else:
        start_time = time.time()
        device = sys.argv[1]
        print ' --- AFL fuzzer ---'
        commands = ['+CCFC=5,4,4239,129,2,/+,18960999,20', '+CCFC=5,4,sadgfas,2,/+,,20', 
                    '+CRLP=691,593,15720364,2448120,20,1012', '+CRLP=,593,efdasfgah,20,1012', 
                    '+CLIP=1', '+CLIP=adfg#$:<@%fd', 
                    '+GSN', '+GSNdag@#$<@%">da', 
                    '+CNEM=1', '+CNEM=ad#$<"@$>?gdasf', 
                    '+CPNSTAT=1', '+CPNSTAT=1', 
                    '+CUSD=0,NH4p,11', '+CUSD=sadasd,NH4p', 
                    '+COPS=0,0,fQ,7', '+COPS=0,0,fQ,7', 
                    '+CPBF=e|Fb|dBSW\I7U}[NeBu.";^*J)Zz>zC;h,.C\'uQ<.c;zvUp;{x5+)w1UhF>VeZ*dMb0DjSFv:ld4c&a~PT3xCP3r2!]oEZ^esWgH-',
                    '+CPBF=e|Fb|dB[NeBu.";^*J)Zz>zC;h,.C\'uQ<.c;zvUp;{x5+)w1UhF>VeZ*dMb0DjSFv:ld4c&a~PT3xCP3r2@>naI98?vh_b!]ogH-', 
                    '+CREG=2', '+CREG=skdfk#@!$%asfjogba',
                    '+CRSM=220,50978,0,0,48348,8H', '+CRSM=adfadsg,0,0sdfag,48348,8H?', 
                    '+CPBR=889592601884112088072906629555,1,}eJ\\=SBn1PpVYcE]`V[l&SJ.#ch)v"bhj%ecD[L#Fn;f@0,0,1',
                    '+CPBR=889592601885397582422910799555,1,}i1tXdhK>:eJLUYP8\']#ch)v"bhj%ecD[L#Fn;f@5=RuK|Z,1,0,0,1', 
                    '+CGDCONT=17,@u,G#oah@,c&28,1,3,1,0,1,0', '+CGDCONT=17,@u,G#oah@,c&28,1,asfasdf,1,0', 
                    '+CCWA=1,2,64', '+CCWA=1,ASD%@$%#$<":Fasd', 
                    '+CMOD=2', '+CMOD=2dassddifg$#%kjkzfag', 
                    '+CAAP=0,0', '+CAAP=SDAMSAF)"$:F,0', 
                    '+CECALL=3', '+CECALL=dga$!%gbdasf,iasasdbga', 
                    '+CGAUTO=1', '+CGAUTO=1dafad<:"}{$!%$gsa',
                    '+CHSU=1', '+CHSU=1adsdfas', 
                    '+CPNET=1', '+CPNET=1gsadgsdjgjyid']
        try:
            fuzz_command(commands, device)
            print '\nExecution time: ', (time.time() - start_time)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print '\nExecution time: ', (time.time() - start_time)
            sys.exit()



def test():
    print ' --- AFL fuzzer ---'
    command = '+CCFC=5,1,1480934,129,8,Pzb;"L,1725093,3'
    print command
    fuzz_command(command, 'test_dev')


if __name__ == '__main__':
    main()
    #test()