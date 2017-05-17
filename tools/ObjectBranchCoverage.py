#!/usr/bin/env python
# ObjectBranchCoverage.py
'''
Measure object branch coverage

first: Dec 9 2016
last : Apr 12 2017

@author Taejoon Byun <taejoon@umn.edu>
'''

import re, sys, IPython, csv, subprocess


class Branch:

    def __init__(self, b_type, ip):
        self._type = b_type             # one of {'J', 'S', 'M', 'L'}
        self.ip = int('0x' + ip, 16)    # instruction pointer
        self._taken = 0                 # taken the jump
        self._fallen = 0                # fallen to the default

    def __str__(self):
        return 'Branch type %s at %s: (%d, %d)' % (self._type, hex(self.ip), 
                self._taken, self._fallen)

    def __repr__(self):
        return self.__str__()

    def get_type(self):
        return self._type

    def get_n_covered(self):
        return sum(self.get_vector())

    def get_vector(self):
        return [1 if self._taken else 0, 1 if self._fallen else 0]

    def get_sat_obligations(self):
        sats = set()
        if self._taken:
            sats.add('1'+str(hex(self.ip)))
        if self._fallen:
            sats.add('0'+str(hex(self.ip)))
        return sats

    def has_taken(self):
        return True if self._taken else False

    def has_fallen(self):
        return True if self._fallen else False

    def update(self, taken, fallen):
        self._taken += taken
        self._fallen += fallen


class ObjectBranchCoverage:


    _TYPES = ['J', 'S', 'M', 'L', 'B']
    _JCC = {'jo', 'jno', 'js', 'jns', 'je', 'jz', 'jne', 'jnz', 
            'jb', 'jnae', 'jc', 'jnb', 'jae', 'jnc', 'jbe', 'jna', 
            'ja', 'jnbe', 'jge', 'jnl', 'jle', 'jng', 'jg', 'jnle', 
            'jp', 'jpe', 'jnp', 'jpo', 'jcxz', 'jecxz'}

    def __init__(self, target_fname, func_list_fname, types='JSML'):
        self._func_list_fname = func_list_fname
        self._target_fname = target_fname
        self._funcs = []         # list of functions to count towards coverage
        self._branches = {}      # {branch_ip: Branch}
        self._coverage = -100.0
        self._file_cnt = 0
        self._type_ip_pairs = []  # (type, ip)
        self._types_to_consider = list(types)
        self._funcs = self._read_function_list()
        self._construct_branch_info()

    def _read_function_list(self):
        with open(self._func_list_fname, 'r') as f:
             return [w.strip() for w in f.readlines()]

    def _construct_branch_info(self):
        try:
            self.get_filtered_dump()
            self._extract_ips_from_dump()
            branches = map((lambda pair: \
                    Branch(pair[0], pair[1])), self._type_ip_pairs)
            self._branches = dict((b.ip, b) for b in branches)
        except Exception as e:
            print 'failure occured during coverage analysis'
            print e

    def get_filtered_dump(self):
        ''' Obtain object dump from the target binary and filter only the 
        functions of concern '''
        CMD = 'objdump -d -M intel-mnemonic %s' % self._target_fname
        DUMP_FNAME = self._target_fname + '.dump'
        dump = None
#        with open(DUMP_FNAME, 'w') as dump_file:
#            subprocess.Popen(CMD, shell=True, stdout=dump_file).communicate()
        p = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE)
        dump = p.stdout.readlines()
        filtered = ''
        keep = False
        for line in dump:
            if any(func in line for func in self._funcs):
                keep = True     # function started
            elif line == "\n":
                keep = False    # function ended
            if keep:
                filtered += line.strip()
        self._dump = filtered

    def _get_instruction_type(self, nm):
        if nm[0] == 'j':
            return 'J' if nm in self._JCC else None
        elif nm[0:4] == 'cmov' or nm[0:4] == 'fcmov':
            return 'M'
        elif nm[0:3] == 'set':
            return 'S'
        elif nm[0:3] == 'and' or nm[0:2] == 'or' or nm[0:3] == 'xor' \
                or nm[0:4] == 'test' or nm[0:3] == 'not':
            return 'L'
        elif nm is 'adc' or nm is 'lock' or nm is 'sbb':
            return 'B'
        else:
            return None

    def _extract_ips_from_dump(self):
        ''' From the dump, extract instruction pointers where conditional
        instruction is '''
        REGEX = r'([0-9a-f]+):\s+[0-9a-f ]+\s([a-z]+)'
        matches = re.findall(REGEX, self._dump)
        if len(matches) == 0:
            raise Exception('The file is not a valid objdump file')
        for match in matches:
            ip = match[0]
            nmemonic = match[1]
            i_type = self._get_instruction_type(nmemonic)
            if i_type is not None and i_type in self._types_to_consider:
                self._type_ip_pairs.append((i_type, ip))

    def update_cov_from_pincov(self, pincov):
        csvf = open(pincov, 'r')
        reader = csv.reader(csvf, delimiter=',')
        next(reader, None)      # skip the header
        for row in reader:
            # type,addr,taken,fallen
            if len(row) == 0:
                raise Exception('The file %s is not a valid pincov file' % 
                        pincov)
            b_type = str(row[0])
            ip = int(row[1], 16)
            if ip in self._branches:
                self._branches[ip].update(int(row[2]), int(row[3]))
        csvf.close()
        self._file_cnt += 1

    def calc_coverage(self):
        assert self._branches is not None and len(self._branches) > 0
        total = len(self._branches) * 2
        covered = 0
        for key, b in self._branches.iteritems():
            covered += b.get_n_covered()
        self._n_covered = covered
        self._coverage = covered / float(total) * 100

    def get_coverage(self):
        if self._coverage < 0:
            self.calc_coverage()
        return self._coverage

    def has_lower_coverage_than(self, another):
        ''' Compare the OBC of two measurements.
        :returns: True if `self` has a lower coverage than `another`.
        '''
        if set(self._branches.keys()) != set(another._branches.keys()):
            raise Exception('not compatible')
        for key in self._branches:
            if self._branches[key].get_n_covered() \
                    < another._branches[key].get_n_covered():
                return True
        return False

    def get_coverage_vector(self):
        ''' Create a vector of 0s and 1s for the branches. Put 1 for a covered 
        decision and 0 for a not covered one.
        '''
        vector = []
        for key in sorted(self._branches.keys()):
            vector += self._branches[key].get_vector()
        return vector

    def get_sat_obligations(self):
        ''' return a set of satisfied obligations '''
        sats = set()
        for key in sorted(self._branches.keys()):
            sats |= self._branches[key].get_sat_obligations()
        return sats

    def get_jump_stats(self):
        if self._coverage < 0:
            self.calc_coverage()
        j_branches = [b for b in self._branches.itervalues() \
                if b.get_type() is 'J']
        n_covered_oblg = sum(map(lambda b: b.get_n_covered(), j_branches))
        return n_covered_oblg, len(j_branches)

    def _percent(self, dividend, divisor):
        a = len(dividend) if type(dividend) in [list, dict] else dividend
        b = len(divisor) if type(divisor) in [list, dict] else divisor
        return 0 if a is 0 or b is 0 else float(a) / float(b) * 100.0

    def get_stats(self):
        ''' return coverage detail as string'''
        if self._coverage < 0:
            self.calc_coverage()
        # group branches by type
        branches_per_type = {t: [] for t in self._TYPES}
        for b in self._branches.itervalues():
            branches_per_type[b.get_type()].append(b)
        # stringify
        ret = str(self) + '\n\n'
        for b_type, branches in branches_per_type.iteritems():
            ret += '- Type %s\n' % b_type
            ret += '\t- cnt: %02.1f %% (%03d / %03d)\n' % \
                    (self._percent(branches, self._branches), \
                    len(branches), len(self._branches))
            n_covered_oblg = sum(map(lambda b: b.get_n_covered(), branches))
            ret += '\t- cov: %02.1f %% (%03d / %03d)\n' % \
                    (self._percent(n_covered_oblg, len(branches)*2), \
                    n_covered_oblg, len(branches)*2)
##TODO: test
        return ret

    def __str__(self):
        if self._coverage < 0:
            self.calc_coverage()
        n_branch = len(self._branches)
        return '%.2f %% OBC, %d / %d (out of %d branches) from %d files'% (
                self._coverage, self._n_covered, n_branch*2, n_branch, self._file_cnt)

def calc_and_print():
    if len(sys.argv) != 4:
        print 'Invalid number of arguments (expected 3)'
        print 'Usage: $ %s <target> <coverage_info> <function_list>, <types>' \
                % sys.argv[0]
        sys.exit()
    obc = ObjectBranchCoverage(sys.argv[1], sys.argv[3], sys.argv[4])
    obc.update_cov_from_pincov(sys.argv[2])
    obc.calc_coverage()
    print obc


def main():
    calc_and_print()

if __name__ == '__main__':
    main()

