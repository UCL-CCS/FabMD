from base.fab import *
from plugins.FabMD.FabMD import *

@task
def lammps_restart(config, results_dir, **args):
    defaults = yaml.load(open(FabMD_path+'/default_settings/lammps.yaml'))
    update_environment(defaults)
    update_environment(args)
    #update_environment(dict(lammps_input="restart.{}".format(env.lammps_input)))

    if "_restart_" in results_dir:
        results_chunks = results_dir.split('_')
        job_number = int(results_chunks[-1])
        job_number += 1
        results_chunks[-1] = str(job_number)
        new_results_dir = '_'.join(results_chunks)
        update_environment({'job_results': new_results_dir, 'job_results_contents_local', new_results_dir})
    else:
        update_environment({'job_results': results_dir + '_restart_1'})
        update_environment({'job_results_contents_local', results_dir + '_restart_1'})

    md_job(config, 'lammps', lammps_input="restart.{}".format(env.lammps_input), job_results=env.job_results, job_results_contents_local=env.job_results_contents_local, **args)



    """
    with_config(config)
    execute(put_configs, config)
    defaults = yaml.load(open(FabMD_path+'/default_settings/'+script+'.yaml'))
    job(dict(script=script,
             wall_time=defaults['wall_time'],
             lammps_input=defaults['lammps_input'],
             cores=defaults['cores'],
             memory='2G'),
        args)
    """
