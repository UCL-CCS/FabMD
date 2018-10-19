import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '../')
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '../../../')

#from deploy.templates import *
#from deploy.machines import *
#from fabric.contrib.project import *
#from base.fab import *

import fileinput

def test_lammps():
    assert( subprocess.call(["fab", "localhost", "lammps:lammps_test1"]) == 0)
  
def test_lammps_ensemble1():
    assert( subprocess.call(["fab", "localhost", "lammps_ensemble:lammps_ensemble_example1,input_name_in_config=data.peptide"]) == 0)

def test_lammps_ensemble2():
    assert( subprocess.call(["fab", "localhost", "lammps_ensemble:lammps_ensemble_example2,input_name_in_config=in.lammps"]) == 0)
