import csv, sys

class MyDictReader(csv.DictReader):
    def next(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames
        row = self.reader.next()
        self.line_num = self.reader.line_num

        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d

outfilename = sys.argv[1]+'.reordered'
with open(sys.argv[1], 'r') as infile, open(outfilename, 'w') \
        as outfile:
    # output dict needs a list for new column ordering
    fieldnames = sys.argv[2].split(',')
    print fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    # reorder the header first
    writer.writeheader()
    for row in MyDictReader(infile):
        # writes the reordered rows to the new file
        writer.writerow(row)

lines = []
with open(outfilename, 'r') as infile:
    lines = infile.readlines()
with open(outfilename, 'w') as outfile:
    for line in lines:
        if ',,' in line:
            outfile.write('\n')
        else:
            outfile.write(line)

