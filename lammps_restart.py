from base.fab import *
from plugins.FabMD.FabMD import *

@task
def lammps_restart(config, **args):
    defaults = yaml.load(open(FabMD_path+'/default_settings/lammps.yaml'))
    update_environment(defaults)
    update_environment(args)
    update_environment(dict(lammps_input="restart.{}".format(env.lammps_input)))
    md_job(config, 'lammps', **args)

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
