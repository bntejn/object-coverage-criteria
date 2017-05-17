# @author Gregory Gay
# Concatinates two Lustre models so that we can check for equivalency

# Written: 08/05/2014
#	- Initial File Creation

# last : Mar 13 2017
# @author Taejoon Byun

#!/usr/bin/python

import os
import sys
import copy
import string
import getopt
import re
from math import *

def main(argv):
    #Default values for command line arguments
    correctModel = ''
    mutantModel = ''
    outputModel = 'combined.lus'

    try:
        opts, args = getopt.getopt(argv,"hc:m:p:")
    except getopt.GetoptError:
        print 'checkEquivalency.py -c <correct model file> -m <mutant model file> -p <filename for combined model>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'checkEquivalency.py -c <correct model file> -m <mutant model file> -p <filename for combined model>'
            sys.exit()
        elif opt == '-c':
            if arg == '':
                raise Exception('No correct model supplied.')
            else:
                correctModel = arg
        elif opt == '-m':
            if arg == '':
                raise Exception('No mutant model supplied.')
            else:
                mutantModel = arg
        elif opt == '-p': 
            outputModel = arg

    if correctModel == '':
        raise Exception('No correct model supplied.')
    if mutantModel == '':
        raise Exception('No mutant model supplied.')

    node=''
    inputs=[]
    outputs=[]
    internal=[]
    expressions=[]

    # Read in correct model
    f=open(correctModel)
    collecting='no'

    for l in f:
        if 'node' in l:
            collecting='inputs'
            found = re.findall("node\s+(\w+)\s*\(\s*(\w+:.*;)", l)[0]
            node = found[0]
            if len(found) == 2:
                inputs.append(found[1]);
        elif 'returns' in l:
            collecting='outputs'
            found = re.findall("returns\s*\(\s*(\w+:.*;)", l)
            if len(found) > 0:
                outputs.append(found[0]);
        elif l.strip()=='var':
            collecting='internal'
        elif l.strip()=='let' or 'let ' in l:
            collecting='expression'
        elif l.strip()=='tel;':
            collecting='no'
        elif collecting=='inputs':
            if l.strip()!='':
                inputs.append(l.strip())
        elif collecting=='outputs':
            if l.strip()!='':
                outputs.append(l.strip().replace(')',''))
        elif collecting=='internal':
            if l.strip()!='':
                internal.append(l.strip())
        elif collecting=='expression':
            if l.strip()!='':
                expressions.append(l)
    f.close()

    # Read in mutant model
    f=open(mutantModel)
    collecting='no'

    variables = [v.split(':')[0] for v in outputs + internal]
    for l in f:
        if 'returns' in l:
            collecting='outputs'
            parts=l.strip().split('(')
            #print 'parts: ' + str(parts)
            outputs.append('m_' + parts[1])
        elif l.strip()=='var':
            collecting='internal'
        elif l.strip()=='let' or 'let ' in l:
            collecting='expression'
        elif l.strip()=='tel;':
            collecting='no'
        elif collecting=='outputs':
            if l.strip()!='':
                outputs.append('m_' + l.strip())
        elif collecting=='internal':
            if l.strip()!='':
                internal.append('m_' + l.strip())
        elif collecting=='expression':
            if l.strip()!='':
                for var in variables:
                    l = l.replace(' '+var, ' m_'+var)
                    l = l.replace('('+var, '(m_'+var)
                expressions.append(l)
    f.close()

    props=[]
    pExp=[]
    numProps=0
    for o in outputs:
        if 'm_' not in o:
            numProps+=1
            pExp.append('\tprop'+str(numProps)+'=('+o.split(':')[0]+' = m_'+o.split(':')[0]+');\n')
            internal.append('prop'+str(numProps)+': bool;')
            #props.append(' --%PROPERTY prop'+str(numProps)+';\n')
    internal.append('propAll: bool;')

    # Combine into new model
    f=open(outputModel,'w')
    f.write('node '+node+'('+inputs[0]+'\n')
    for i in range(1,len(inputs)):
        f.write('\t'+inputs[i]+'\n')

    f.write('returns ('+outputs[0]+'\n')
    for o in range(1,len(outputs)):
        f.write('\t'+outputs[o]+'\n')

    f.write('var\n')
    for i in internal:
        f.write('\t'+i+'\n')
    f.write('let\n')
    for e in expressions:
        f.write(e)

    pE=''
    numProps=0
    for p in pExp:
        f.write(p)
        numProps+=1
        if numProps==1:
            pE='prop1'
        else:
            pE='('+pE+' and prop'+str(numProps)+')'

    f.write('\tpropAll='+pE+';\n')

    f.write(' --%PROPERTY propAll;\n')
    #for p in props:
            #f.write(p)
    f.write('tel;\n')
    f.close()

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
