# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is
# distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabNanoMD.
# authors:
#           Hamid Arabnejad, Robbie Sinclair, Derek Groen, Maxime Vassaux,
#           and Werner Müller

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from pprint import pprint
import os
import yaml
import ruamel.yaml
from plugins.FabMD.gromacs_ensembles import *
from plugins.FabMD.lammps_restart import *

# Add local script, blackbox and template path.
add_local_paths("FabMD")

FabMD_path = get_plugin_path('FabMD')


@task
@load_plugin_env_vars("FabMD")
def lammps(config, **args):
    """
    fab localhost lammps:lammps_test1
    """
    env.update(env.lammps_params)
    return md_job(config, 'lammps', **args)


@task
@load_plugin_env_vars("FabMD")
def namd(config, **args):
    """
    fab localhost namd:namd_test1
    """
    env.update(env.namd_params)
    return md_job(config, 'namd', **args)


@task
@load_plugin_env_vars("FabMD")
def gromacs(config, grompp=None, conf=None, topol=None, **args):
    """
    fab localhost gromacs:gromacs_test
    """
    env.update(env.gromacs_params)
    # overwrite env.required_files dict with user input values
    if grompp is not None:
        env.required_files['grompp'] = grompp
    if conf is not None:
        env.required_files['conf'] = conf
    if topol is not None:
        env.required_files['topol'] = topol

    env.grompp_command = make_grompp_command(config, **args)
    return md_job(config, 'gromacs', **args)


def md_job(config, script, **args):
    """
    Submit an MD job
    input args

        script:
            input script for job execution,
            available scripts : lammps or gromacs
        config:
            config directory to use to define geometry
            please look at /FabMD/config_files to see the available configs
    """
    update_environment(args)
    with_config(config)
    execute(put_configs, config)
    return job(dict(script=script,
                    memory='2G'),
               args)


@task
@load_plugin_env_vars("FabMD")
def lammps_ensemble(config, sweep_dir=False, **kwargs):
    '''
        fab localhost lammps_ensemble:lammps_ensemble_example1
        fab localhost lammps_ensemble:lammps_ensemble_example2

    https://github.com/UCL-CCS/FabMD/blob/hamid-dev/doc/RunEnsemble-examples.md
    '''
    env.update(env.lammps_params)
    md_ensemble(config, 'lammps', sweep_dir, **kwargs)


@task
@load_plugin_env_vars("FabMD")
def gromacs_ensemble(config, grompp=None, conf=None, topol=None,
                     sweep_dir=False, **kwargs):
    env.update(env.gromacs_params)
    # overwrite env.required_files dict with user input values
    if grompp is not None:
        env.required_files['grompp'] = grompp
    if conf is not None:
        env.required_files['conf'] = conf
    if topol is not None:
        env.required_files['topol'] = topol

    env.grompp_command = make_grompp_command(config, kwargs)
    md_ensemble(config, 'gromacs', sweep_dir, kwargs)


def md_ensemble(config, script, sweep_dir, **kwargs):

    # If sweep_dir not set assume it is a directory in config with default name
    if sweep_dir is False:
        path_to_config = find_config_file_path(config)
        sweep_dir = os.path.join(path_to_config, env.sweep_dir_name)

    env.script = script
    with_config(config)
    run_ensemble(config, sweep_dir, **kwargs)


def make_grompp_command(config, **args):
    config_dir = find_config_file_path(config)
    required_files = {'grompp': {'extension': '.mdp', 'flag': 'f'},
                      'conf': {'extension': '.gro', 'flag': 'c'},
                      'topol': {'extension': '.top', 'flag': 'p'}}
    optional_files = {'checkpoint': {'extension': '.cpt', 'flag': 't'},
                      'index': {'extension': '.ndx', 'flag': 'n'}}

    grompp_args = {}
    for reqfile in required_files:
        flag = required_files[reqfile]['flag']

        # specified as default?
        if reqfile in env.required_files:
            if env.required_files[reqfile]:
                grompp_args[flag] = env.required_files[reqfile]
                continue

        # find file in config directory with the correct extension?
        possible_files = []
        for file_ in os.listdir(config_dir):
            if file_.endswith(required_files[reqfile]['extension']):
                possible_files += [file_]
        if len(possible_files) > 1:
            print('=====')
            print('Found multiple possible', reqfile, 'files:')
            print(possible_files)
            print('Specify which to use')
        elif len(possible_files) == 1:
            grompp_args[flag] = possible_files[0]
            continue

        # no file found, warn user and exit
        print('Could not find a ', reqfile, 'file.')
        sys.exit()

    for optfile in optional_files:
        flag = optional_files[optfile]['flag']
        if optfile in env.required_files:
            if env.required_files[optfile]:
                grompp_args[flag] = env.required_files[optfile]
                continue

    grompp_command = ''
    for arg in grompp_args:
        grompp_command += '-' + arg + ' ' + grompp_args[arg] + ' '
    print('grompp arguments = ', grompp_command)
    return grompp_command


@task
@load_plugin_env_vars("FabMD")
def lammps_init_campaign(config, **args):
    """
    fab localhost lammps_init_campaign:fabmd_easyvvuq_test1
    fab eagle_hidalgo lammps_init_campaign:fabmd_easyvvuq_test1
    """
    update_environment(args)
    with_config(config)
    # to prevent mixing with previous campaign runs
    env.prevent_results_overwrite = "delete"
    execute(put_configs, config)

    # adds a label to the generated job folder
    job_lable = 'init_campaign'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    env.script = 'lammps_init_campaign'
    job(args)


@task
@load_plugin_env_vars("FabMD")
def lammps_run_campaign(config, **args):
    """
    fab localhost lammps_run_campaign:fabmd_easyvvuq_test1
    fab eagle_hidalgo lammps_run_campaign:fabmd_easyvvuq_test1
    """
    update_environment(args)
    with_config(config)
    path_to_config = find_config_file_path(config)
    print("local config file path at: %s" % path_to_config)

    path_to_config_on_remote_host = env.job_config_path
    print("remote config file path at: %s" % path_to_config_on_remote_host)

    sweep_dir = path_to_config_on_remote_host + "/SWEEP"
    env.script = 'lammps'

    # adds a label to the generated job folder
    job_lable = 'run_campaign'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    env.update(env.lammps_params)
    run_ensemble(config, sweep_dir, sweep_on_remote=True,
                 execute_put_configs=False, **args)


@task
@load_plugin_env_vars("FabMD")
def lammps_analyse_campaign(config, **args):
    """
    fab localhost lammps_analyse_campaign:fabmd_easyvvuq_test1
    fab eagle_hidalgo lammps_analyse_campaign:fabmd_easyvvuq_test1
    """
    update_environment(args)
    with_config(config)

    job_lable = 'run_campaign'
    env.src_campaign_dir = os.path.join(env.results_path, template(
        env.job_name_template) + '_{}'.format(job_lable))

    job_lable = 'init_campaign'
    env.dst_campaign_dir = os.path.join(env.results_path, template(
        env.job_name_template) + '_{}'.format(job_lable))

    # adds a label to the generated job folder
    job_lable = 'analyse_campaign'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    # env.TestOnly = 'True'
    env.script = 'lammps_analyse_campaign'
    job(args)

    # print(template(env.job_name_template))
    # pprint(env)


@task
@load_plugin_env_vars("FabMD")
def namd_init_campaign(config, **args):
    """
    fab localhost namd_init_campaign:BAC
    fab eagle_hidalgo namd_init_campaign:BAC
    """
    update_environment(args)
    with_config(config)
    # to prevent mixing with previous campaign runs
    env.prevent_results_overwrite = "delete"
    execute(put_configs, config)

    # adds a label to the generated job folder
    job_lable = 'init_campaign'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    # read config param from yaml file
    path_to_config = find_config_file_path(config)
    campaign_config = yaml.load(open(os.path.join(path_to_config,
                                                  'campaign_config',
                                                  'campaign_config.yml')),
                                Loader=yaml.SafeLoader
                                )
    env.app_name = campaign_config['app_name']

    env.script = 'namd_init_campaign'
    job(args)


@task
@load_plugin_env_vars("FabMD")
def namd_run_campaign(config, **args):
    """
    fab localhost namd_run_campaign:BAC
    fab eagle_hidalgo namd_run_campaign:BAC
    """

    update_environment(args)
    with_config(config)
    path_to_config = find_config_file_path(config)
    print("local config file path at: %s" % path_to_config)
    path_to_config_on_remote_host = env.job_config_path
    print("remote config file path at: %s" % path_to_config_on_remote_host)

    env.script = 'namd_full'

    # adds a label to the generated job folder
    job_lable = 'run_campaign'
    # job_name_template: ${config}_${machine_name}_${cores}
    env.job_name_template += '_{}'.format(job_lable)

    env.update(env.lammps_params)

    # read config param from yaml file
    campaign_config = yaml.load(open(os.path.join(path_to_config,
                                                  'campaign_config',
                                                  'campaign_config.yml')),
                                Loader=yaml.SafeLoader
                                )
    env.app_name = campaign_config['app_name']
    env.n_replicas = campaign_config['n_replicas']

    # For NAMD application, the actual config files directory is located in :
    #                   campaign_config/templates/<app_name> subdirectory
    # so, we overwrite some env parameters generated by with_config()
    env.job_config_path = os.path.join(env.job_config_path,
                                       'campaign_config',
                                       'templates',
                                       env.app_name)

    sweep_dir = os.path.join(path_to_config_on_remote_host,
                             'campaign_config',
                             'templates',
                             env.app_name,
                             'SWEEP')

    run_ensemble(config, sweep_dir, sweep_on_remote=True,
                 execute_put_configs=False, **args)


def get_FabMD_tmp_path():
    """ Creates a directory within FabMD for file manipulation
    Once simulations are completed, its contents can be removed"""
    tmp_path = FabMD_path + "/tmp"
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    return tmp_path
