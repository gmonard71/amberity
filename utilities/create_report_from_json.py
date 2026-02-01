#!/usr/bin/env python3

"""create a report page from log files

Workflow:
./create_report_from_json.py *.json
"""

import json
import sys
import yaml
import argparse

def parser():
    parser = argparse.ArgumentParser(description='Create a report page in markdown from log files.')
    parser.add_argument('--header', type=str, help='Markdown header file', required=False)
    parser.add_argument('--footer', type=str, help='Markdown footer file', required=False)
    parser.add_argument('logs', nargs='+', help='List of logs to process')

    args = parser.parse_args()

    return args

args = parser()


content = []
for fn in args.logs:
   #print(fn)
    with open(fn,'r') as fp:
        data = json.load(fp)
        content.append(data)

if args.header:
    with open(args.header,'r') as f: header=f.read()
else:
    header=""

if args.footer:
    with open(args.footer,'r') as f: footer=f.read()
else:
    footer=""

def markdown():
    print("## Installation using cmake\n")
    print("| Container OS | cmake_configure | install | # bin files | # installed files |")
    print("| ------------ | --------------- | ------- | ----------- | ----------------- |")
    for image in content:
        name=image['image']
        cmake = {True:':white_check_mark:', False: ':x:'}[image['check']['cmake']]
        build = {True:':white_check_mark:', False: ':x:'}[image['check']['build']]
        bins = image['check']['walk']['bin']
        files = image['check']['walk']['total']
        line = "| {:23} | {} | {} | {} | {} |".format(name,cmake,build,bins,files)
        print(line)

    def error_fmt(d,key):
        if key not in d: return "-/-/-"
        mystr = "**{}**".format(d[key]['passed'])
        if d[key]['failed'] == 0:
           mystr += "/0"
        else:
           mystr += "/[+ {} +]".format(d[key]['failed'])
        if d[key]['error'] == 0:
           mystr += "/0"
        else:
           mystr += "/[- {} -]".format(d[key]['error'])
        return mystr

    print("""
## CPU test results

results are displayed as **passed**/[+ failed +]/[- errors -]
""")

    print("| Container OS | at_serial | at_openmp | at_parallel | amber_serial | amber_parallel |")
    print("| ------------ | --------- | --------- | ----------- | ------------ | -------------- |")

    for image in content:
        name=image['image']
        line = "| {name:23} | {at_serial} | {at_openmp} | {at_parallel} | {amber_serial} | {amber_parallel} |"
        fmt = {}
        fmt['name'] = name
        fmt['at_serial'] = error_fmt(image['test'],'at_serial')
        fmt['at_openmp'] = error_fmt(image['test'],'at_openmp')
        fmt['at_parallel'] = error_fmt(image['test'],'at_parallel')
        fmt['amber_serial'] = error_fmt(image['test'],'amber_serial')
        fmt['amber_parallel'] = error_fmt(image['test'],'amber_parallel')
        print(line.format(**fmt))

    print("""
## GPU test results

results are displayed as **passed**/[+ failed +]/[- errors -]
""")

    print("| Container OS | at_cuda_serial | amber_cuda_serial | amber_cuda_parallel |")
    print("| ------------ | -------------- | ----------------- | ------------------- |")
    for image in content:
        if 'at_cuda_serial' not in image['test'] and 'amber_cuda_serial' not in image['test']: continue # this is not a GPU container
        name=image['image']
        line = "| {name:23} | {at_cuda_serial} | {amber_cuda_serial} | {amber_cuda_parallel} |"
        fmt = {}
        fmt['name'] = name
        fmt['at_cuda_serial'] = error_fmt(image['test'],'at_cuda_serial')
       #fmt['at_cuda_parallel'] = error_fmt(image['test'],'at_cuda_parallel')
        fmt['amber_cuda_serial'] = error_fmt(image['test'],'amber_cuda_serial')
        fmt['amber_cuda_parallel'] = error_fmt(image['test'],'amber_cuda_parallel')
        print(line.format(**fmt))

    print("""
## Container information

Note:

- cmake is pre-installed in each container using a binary downloaded from cmake.org
- due to some "bad" implementation of MPI on some OSes, MPI is installed locally using the `configure_openmpi` script
""")

    print("| Container OS | cmake | python(miniconda) | compiler | MPI |")
    print("| ------------ | ----- | ----------------- | -------- | ------- |")
    for image in content:
        details={'name': image['image'],
                 'cmake': image['cmake']['version'],
                 'python': image['python']['version'],
                 'compiler': image['compiler']['name']+' '+image['compiler']['version'],
                }
        if 'mpi' in image: 
            details['mpi']= image['mpi']['name']+' '+image['mpi']['version']
        else:
            details['mpi']= 'N/A'
        line = "| {name:23} | {cmake} | {python} | {compiler} | {mpi} |".format(**details)
        print(line)

print(header)
markdown()
print(footer)
