from base.fab import *
from plugins.FabMD.FabMD import *

@task
def lammps_restart(config, results_dir, **args):
    defaults = yaml.load(open(FabMD_path+'/default_settings/lammps.yaml'))
    update_environment(defaults)
    update_environment(args)

    job_number = 1
    if "restart_" in results_dir:
        results_chunks = results_dir.split('_')
        job_number = int(results_chunks[1]) #  results_dir starts with 'restart_<x>'.
        job_number += 1

    if hasattr(env, "label"):
        env.label += "_restart_{}".format(job_number)
    else:
        env.label = "restart_{}".format(job_number)

    # Assumption: runs are continued on the same machine.
    env.run_prefix_commands = ["cp -r $previous_job_results/lammps.restart $job_results/"]
    
    pjr = "{}/../{}".format("$job_results", results_dir)

    md_job(config, 'lammps', lammps_input="restart.{}".format(env.lammps_input), label=env.label, run_prefix_commands=env.run_prefix_commands, previous_job_results=pjr, **args)


