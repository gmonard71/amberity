#!/usr/bin/env python3

"""
Create a report from within a singularity container about configuration, building and testing of Amber
"""

import os
import sys
import platform
import subprocess
import json

#print(sys.argv)
image_name = sys.argv[1]
amber_source=sys.argv[2]
amber_install=sys.argv[3]
compiler=sys.argv[4]

#print("Source: {}".format(amber_source))
#print("Installation: {}".format(amber_install))
#print("Compiler: {}".format(compiler))

#-os version
#-compiler version + which
#-mpi version + which
#-python version
#-cmake version

# has cmake succeeded?
# has build succeeded?
# number of bin files
# number of installed files

# passed/failed/errors
# test.serial
# test.openmp
# test.mpi
# test.cuda.serial
# test.cuda.mpi

def cmd(thecommand):
    python_version = platform.python_version().split('.')
    if int(python_version[1]) >= 7:
        ret = subprocess.run(thecommand,check=True,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    else:
        ret = subprocess.run(thecommand,check=True,shell=True,universal_newlines=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return ret


specs = {'image': image_name}

# OS Version
#try:
#    theplatform = platform.freedesktop_os_release()
#    os_name = theplatform['ID']
#    os_version = theplatform['VERSION_ID']
#except:
ret = cmd('cat /etc/os-release | grep "^ID="')
os_name = ret.stdout[:-1].split('=')[-1]
ret = cmd('cat /etc/os-release | grep "^VERSION_ID="')
os_version = ret.stdout[:-1].split('=')[-1]
specs['os'] = {'name': os_name, 'version': os_version}

# Python version
python_version = platform.python_version()
specs['python'] = {'version': python_version}

# Cmake version
ret = cmd('cmake --version')
cmake_version = ret.stdout.split('\n')[0].split()[-1]
specs['cmake'] = {'version': cmake_version}

# Compiler version
if compiler == 'gnu':
    ret = cmd('gcc --version')
    compiler_version=ret.stdout.split()[2]
    specs['compiler'] = {'name': 'gcc', 'version': compiler_version }
if compiler == 'intel':
    ret = cmd('icx -v')
    compiler_version=ret.stdout.split()[2]
    specs['compiler'] = {'name': 'intel', 'version': compiler_version }
if compiler == 'clang':
    ret = cmd('clang -v')
    compiler_version=ret.stdout.split()[3]
    specs['compiler'] = {'name': 'clang', 'version': compiler_version }

# MPI version
try:
    ret = cmd('which mpirun')
except:
    ret = None
if ret is not None:
    ret = cmd('mpirun --version')
    data = ret.stdout.split()
    if 'Intel(R)' in data:
        i = data.index('Version')
        mpi_version = data[i+1]
        specs['mpi'] = {'name': 'intel', 'version': mpi_version}
    if '(Open' in data:
        mpi_version = data[3]
        specs['mpi'] = {'name': 'openmpi', 'version': mpi_version}

# Has cmake succeeded
specs['check'] = {'cmake': False}
cmake_log_path = os.path.join(amber_source,'build','cmake.log')
if os.path.exists(cmake_log_path):
    with open(cmake_log_path,'rb') as f:
       #lines = f.readlines()
        for line in f:
            if b'Configuring incomplete, errors occurred!' in line: break
            if b'Cleaning source directories.\n' in line: specs['check'] = {'cmake': True}

# Has build succeeded
specs['check']['build'] = False
install_path = os.path.join(amber_source,'build','install_manifest.txt')
if os.path.exists(install_path):
    specs['check']['build'] = True
#    with open(install_path,'r') as f:
#        lines = f.readlines()
#        total_lines = len(lines)
#        bin_lines = 0
#        for line in lines:
#            if line.startswith(os.path.join(amber_install,'bin')): bin_lines += 1
#        specs['check']['build'] = {'total': total_lines, 'bin': bin_lines}
total_lines = 0
bin_lines = 0
for root, dirs, files in os.walk(amber_install):
    if root.startswith(os.path.join(amber_install,'bin')):
        bin_lines += len(files)
    total_lines += len(files)
specs['check']['walk'] = {'total': total_lines, 'bin': bin_lines}

# test.serial
specs['test'] = {'at_serial': 'N/A',
                 'at_openmp': 'N/A',
                 'at_parallel': 'N/A',
                 'at_cuda_serial': 'N/A',
                 'amber_serial': 'N/A',
                 'amber_parallel': 'N/A',
                 'amber_cuda_serial': 'N/A',
                 'amber_cuda_parallel': 'N/A',
                }
def test_check(test_dir):
    for root, dirs, files in os.walk(os.path.join(amber_install,'logs',test_dir)):
        log = sorted([x for x in files if x.endswith('.log')])[-1]
        with open(os.path.join(root,log)) as f:
            for line in f:
                if 'file comparisons passed' in line: passed = line.split()[0]
                if 'file comparisons failed' in line: failed = line.split()[0]
                if 'tests experienced an error' in line: errors = line.split()[0]
                if 'tests experienced errors' in line: errors = line.split()[0]
            return {'passed': passed,'failed': failed,'error': errors}
    return 'N/A'
specs['test']['at_serial']           = test_check('test_at_serial')
specs['test']['at_openmp']           = test_check('test_at_openmp')
specs['test']['at_parallel']         = test_check('test_at_parallel')
specs['test']['at_cuda_serial']      = test_check('test_at_cuda_serial')
specs['test']['at_cuda_parallel']    = test_check('test_at_cuda_parallel')
specs['test']['amber_serial']        = test_check('test_amber_serial')
specs['test']['amber_parallel']      = test_check('test_amber_parallel')
specs['test']['amber_cuda_serial']   = test_check('test_amber_cuda_serial')
specs['test']['amber_cuda_parallel'] = test_check('test_amber_cuda_parallel')
# keep only the non-'N/A'
thefilter = {}
for k,v in specs['test'].items():
    if specs['test'][k] != 'N/A': thefilter[k] = v
specs['test'] = thefilter

with open(os.path.join(amber_source,'..','report.json'),'w') as fp:
    json.dump(specs,fp,indent=4)
print(json.dumps(specs,indent=4))
