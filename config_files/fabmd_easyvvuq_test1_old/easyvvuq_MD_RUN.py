#!/usr/bin/env python3


import json
import numpy as np
import os
import sys
import signal
import subprocess
import time
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
# c_work_dir = os.path.join(work_dirx, lmp_input)
# host = 'localhost'
# # execute = uq.actions.ExecuteLocal(
# #     "fabsim  {}  lammps_run_campaign:fabmd_easyvvuq_test1, lammps_input={}".format(host, campaign_params['encoder_target_filename'])
# # )
# # execute = uq.actions.ExecuteLocal(
# #     "fabsim  {}  lammps_run_campaign:fabmd_easyvvuq_test1".format(host)
# # )@task
# @load_plugin_env_vars("FabMD")
import shutil
import tempfile
from ruamel.yaml import YAML
from pathlib import Path

with open(lmp_input, "r") as f:

    try:
       print("Executing easyvvuq with FabMD ...")
       work_dirx = os.path.dirname(os.path.abspath(__file__))
       first = os.listdir('..')[0]
       sec = os.listdir('../..')[0]
       print('c_path', c_path)
       lm1 = c_path + '/' + str(sec) + '/' + str(first) + '/'
       pep2 = c_path + '/' + str(sec) + '/' + str(first) + '/SWEEP/peptide1/data.peptide'
       pep2x = c_path + '/' + str(sec) + '/' + str(first) + '/SWEEP'
       pep2xx = c_path + '/' + str(sec) + '/' + str(first) + '/SWEEP' + '/peptide1'
       os.system('mkdir {}'.format(pep2x))
       os.system('mkdir {}'.format(pep2xx))
       print('two_dir_up_ ', two_dir_up_)
       from pathlib import Path

       px = os.listdir(two_dir_up_ + '/config_files')

       pep1 = two_dir_up_ + '/config_files/' + px[0] + '/SWEEP/peptide1/data.peptide'
       # os.system('cp  {}  {}'.format( pep2, pep1))
       print('pep1', pep1)
       print('pep2', pep2)
       print('c_path', c_path)
       print('work_dirx', work_dirx)
       print('first', first)
       print('sec', sec)
       # dirname1 = tempfile.mktemp(pep2)
       shutil.copy(os.path.join(pep1), os.path.join(pep2))
       c_work_dir = os.path.join(lm1, lmp_input)
       print('c_work_dir', c_work_dir)

       # / Users / kevinbronik / lammps / src / lmp_serial < in.lammps > log.lammps
       process = subprocess.Popen(['/Users/kevinbronik/lammps/src/lmp_serial', '-i',  c_work_dir],
                                      stdout=subprocess.PIPE,
                                      universal_newlines=True)
# '/Users/kevinbronik/FabSim3/localhost_exe/FabSim/results/fabmd_easyvvuq_test1_localhost_1_run_campaign/RUNS/peptide1/output.csv'
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


    except:
         print("system error, terminating!")
         time.sleep(1)
         os.kill(os.getpid(), signal.SIGTERM)
# output_filename