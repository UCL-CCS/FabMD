#!/usr/bin/env python3


import json
import numpy as np
import os
import sys
import signal
import subprocess
import time
import shlex
import platform
import xml.etree.ElementTree as ET
import pandas as pd

work_dirx = os.path.dirname(os.path.abspath(__file__))
# c_work_dir = os.path.join(work_dirx, 'in.lammps')
from pathlib import Path
curr_dir=Path(os.path.dirname(os.path.abspath(__file__)))
two_dir_up_=os.fspath(Path(curr_dir.parent.parent).resolve())
lmp_input = sys.argv[1]
c_path = sys.argv[2]
import shutil
import tempfile
from ruamel.yaml import YAML
from pathlib import Path

try:
    commandstring = ''

    for arg in sys.argv[3:]:
            if ' ' in arg:
                  commandstring+= '"{}"  '.format(arg)    # Put the quotes back in

            else:
                  commandstring+="{}  ".format(arg)

    lammps_exec = commandstring.split(sep=',').pop(2)
    lammps_exec = lammps_exec.replace("'", "").strip()

    run_command = commandstring.split(sep=',').pop(1)
    run_command = run_command.replace("'", "").strip()
    run_command = run_command.split()

    lammps_args = commandstring.split(sep=',').pop(3)
    lammps_args = lammps_args.replace("'", "").strip()
    lammps_args = lammps_args.split()
    string = lammps_exec
    run_command.append(string)
    for i in range(0, len(lammps_args)):
        run_command.append(lammps_args[i])


    run_command.append('-in')
    # print('run_command before final substitution:', run_command)
# mpirun -np 16 lmp_mpi -var f tmp.out -log log.lammps -screen none -in in.lammps

except:
         print("system error, terminating!")
         time.sleep(1)
         os.kill(os.getpid(), signal.SIGTERM)


try:
       print("Executing easyvvuq with FabMD ...")
       # work_dirx = os.path.dirname(os.path.abspath(__file__))
       first = os.listdir('..')[0]
       sec = os.listdir('../..')[0]
       lm1 = c_path + '/' + str(sec) + '/' + str(first) + '/'
       px = os.listdir(two_dir_up_)
       pep1 = work_dirx + '/data.peptide'
       # print('pep1', pep1)
       pep2 = c_path + '/' + str(sec) + '/' + str(first) + '/data.peptide'
       pv = c_path + '/' + str(sec) + '/' + str(first) + '/output.csv'
       # print('pep2', pep2)
       shutil.copy(os.path.join(pep1), os.path.join(pep2))
       pep1x = work_dirx + '/parseLammpsLog.py'
       pep2x = c_path + '/' + str(sec) + '/' + str(first) + '/parseLammpsLog.py'
       shutil.copy(os.path.join(pep1x), os.path.join(pep2x))

       c_work_dir = os.path.join(lm1, lmp_input)
       c_work_dirx = os.path.join(lm1, 'log.lammps')

       # / Users / kevinbronik / lammps / src / lmp_serial < in.lammps > log.lammps
       # process = subprocess.Popen(['/Users/kevinbronik/lammps/src/lmp_serial', '-i',  lmp_input],
       #                                stdout=subprocess.PIPE,
       #                                universal_newlines=True)
       # commmand ='mpirun', '-np', '1', string, '-i', lmp_input
       # run_commandx = ['mpirun', '-np', '1']
       # commmand = string, '-i', lmp_input



       run_command.append(lmp_input)

       process = subprocess.Popen(run_command,
                                      stdout=subprocess.PIPE,
                                      universal_newlines=True)
       # lammps_exec = ''
       while True:
               output = process.stdout.readline()
               print(output.strip())
               # Do something else
               return_code = process.poll()
               if return_code is not None:
                   print('RETURN CODE', return_code)
                   # Process has finished, read rest of the output
                   for output in process.stdout.readlines():
                       print(output.strip())
                   break

       process1 = subprocess.Popen(['python3',  os.path.join(pep2x)],
                                      stdout=subprocess.PIPE,
                                      universal_newlines=True)

       while True:
               output = process1.stdout.readline()
               print(output.strip())
               # Do something else
               return_code = process1.poll()
               if return_code is not None:
                   print('RETURN CODE', return_code)
                   # Process has finished, read rest of the output
                   for output in process1.stdout.readlines():
                       print(output.strip())
                   break


except:
         print("system error, terminating!")
         time.sleep(1)
         os.kill(os.getpid(), signal.SIGTERM)