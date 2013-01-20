import argparse
import csv
import dataconverters.commas as dcsv
import urllib2
import mimetypes
import sys


def main():
    parser = argparse.ArgumentParser(description=\
'''Convert data from one format to another.

Supported input formats: csv, tsv, excel (xls, xlsx).
Supported output formats: csv, json

Examples
========

dataconvert https://github.com/okfn/dataconverters/raw/master/testdata/xls/simple.xls out.csv

Help
====
''',
    epilog='''Copyright Open Knowledge Foundation 2007-2013. Licensed under the
 MIT license. Part of the DataConverters project:
 https://github.com/okfn/dataconverters''',
     formatter_class=argparse.RawDescriptionHelpFormatter
)
    parser.add_argument('inpath', metavar='inpath', type=str,
                       help='in file path or url')
    parser.add_argument('outpath', metavar='outpath', type=str,
                       help='out file path to write to (use underscore "_" as filename to indicate stdout e.g. _.csv or _.json)')
    parser.add_argument('--no-guess-types', dest='guess_types',
        action='store_false',
        help='''Disable type-guessing (where it is used e.g. with CSVs). Type guessing may significantly affect performance''',
        default=True
        )

    args = parser.parse_args()
    intype = guess_type(args.inpath)
    outtype = guess_type(args.outpath)

    if is_url_path(args.inpath):
        instream = urllib2.urlopen(args.inpath)
    else:
        instream = open(args.inpath)

    # tsv_types = ['tsv', 'text/tsv', 'text/tab-separated-values']
    if intype == 'text/csv':
        records, metadata = dcsv.parse(instream, guess_types=args.guess_types)
    elif intype in ['application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
        import dataconverters.xls
        excel_type = 'xls' if intype == 'application/vnd.ms-excel' else 'xlsx'
        records, metadata = dataconverters.xls.parse(instream,
                excel_type=excel_type,
                guess_types=args.guess_types)
    else:
        raise ValueError(
            'No support for reading file type %s - support for csv or xls only at present' % intype)

    if args.outpath.startswith('_.'):
        outstream = sys.stdout
    else:
        outstream = open(args.outpath, 'w')

    if outtype == 'text/csv':
        dcsv.write(outstream, records, metadata)
    elif outtype == 'application/json':
        import dataconverters.jsondata as js
        js.write(outstream, records, metadata)
    else:
        print 'Only support writing to csv and json at present'

def guess_type(path):
    out = mimetypes.guess_type(path)
    return out[0]

def is_url_path(path):
    schemes = ['http', 'https', 'ftp'] 
    for s in schemes:
        if path.startswith(s + '://'):
            return True
    return False

if __name__ == '__main__':
    main()
