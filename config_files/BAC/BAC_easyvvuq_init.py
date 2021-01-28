#
# This file contains easyvvuq definitions specific for FabMD plugin.
# author: Hamid Arabnejad
#
import os
import yaml
import math
import ruamel.yaml
from pprint import pprint
from shutil import rmtree
import json
import chaospy as cp
import numpy as np
import tempfile
import easyvvuq as uq
from encoders import SimEncoder, Eq0Encoder, Eq1Encoder, Eq2Encoder


work_dir = os.path.dirname(os.path.abspath(__file__))
campaign_config_dir = os.path.join(work_dir, 'campaign_config')


def init_campaign():

    #############################################
    # load campaign configuration from yml file #
    #############################################
    campaign_config = load_campaign_config()

    campaign_name = 'BAC_%s' % (campaign_config['sampler_name'])
    campaign_work_dir = os.path.join(work_dir,
                                     'BAC_easyvvuq_%s' % (
                                         campaign_config['sampler_name'])
                                     )

    ######################################
    # delete campaign_work_dir is exists #
    ######################################
    if os.path.exists(campaign_work_dir):
        rmtree(campaign_work_dir)
    os.makedirs(campaign_work_dir)

    ###########################
    # Set up a fresh campaign #
    ###########################
    db_location = "sqlite:///" + campaign_work_dir + "/campaign.db"
    campaign = uq.Campaign(name=campaign_name,
                           db_location=db_location,
                           work_dir=campaign_work_dir)

    #################################
    # Create an encoder and decoder #
    #################################
    n_replicas = campaign_config['n_replicas']
    directory_tree = {
        'build': None,
        'constraint': None,
        'fe': {
            'build': None,
            'dcd': None,
            'mmpbsa': {
                'rep' + str(i): None for i in range(1, n_replicas + 1)
            },
        },
        'par': None,
        'replica-confs': None,
        'replicas': {
            'rep' + str(i): {
                'equilibration': None,
                'simulation': None
            }
            for i in range(1, n_replicas + 1)
        }
    }

    src_confs = os.path.join(campaign_config_dir,
                             'templates',
                             campaign_config['app_name'],
                             'replica-confs'
                             )
    dst_confs = os.path.join('replica-confs')

    multiencoder = uq.encoders.MultiEncoder(
        uq.encoders.DirectoryBuilder(tree=directory_tree),
        Eq0Encoder(
            template_fname=os.path.join(src_confs, 'template_eq0.conf'),
            target_filename=os.path.join(dst_confs, 'eq0.conf')),
        uq.encoders.CopyEncoder(
            source_filename=os.path.join(src_confs, 'eq0-replicas.conf'),
            target_filename=os.path.join(dst_confs, 'eq0-replicas.conf')),
        Eq1Encoder(
            template_fname=os.path.join(src_confs, 'template_eq1.conf'),
            target_filename=os.path.join(dst_confs, 'eq1.conf')),
        uq.encoders.CopyEncoder(
            source_filename=os.path.join(src_confs, 'eq1-replicas.conf'),
            target_filename=os.path.join(dst_confs, 'eq1-replicas.conf')),
        Eq2Encoder(
            template_fname=os.path.join(src_confs, 'template_eq2.conf'),
            target_filename=os.path.join(dst_confs, 'eq2.conf')),
        uq.encoders.CopyEncoder(
            source_filename=os.path.join(src_confs, 'eq2-replicas.conf'),
            target_filename=os.path.join(dst_confs, 'eq2-replicas.conf')),
        SimEncoder(
            template_fname=os.path.join(src_confs, 'template_sim1.conf'),
            target_filename=os.path.join(dst_confs, 'sim1.conf')),
        uq.encoders.CopyEncoder(
            source_filename=os.path.join(src_confs, 'sim1-replicas.conf'),
            target_filename=os.path.join(dst_confs, 'sim1-replicas.conf')),
        uq.encoders.GenericEncoder(
            delimiter=campaign_config['encoder_delimiter'],
            template_fname=os.path.join(
                campaign_config_dir, 'templates', campaign_config['app_name'],
                'build', 'tleap.in'),
            target_filename=os.path.join('build', 'tleap.in'))
    )

    decoder = uq.decoders.SimpleCSV(
        target_filename=campaign_config['decoder_target_filename'],
        output_columns=campaign_config['decoder_output_columns'], header=0, delimiter=','
    )

    collater = uq.collate.AggregateSamples(average=False)

    ###################
    # Add the BAC app #
    ###################
    campaign.add_app(name=campaign_name,
                     params=campaign_config['params'],
                     encoder=multiencoder,
                     collater=collater,
                     decoder=decoder)
    # campaign.set_app(campaign_name)

    ######################
    # parameters to vary #
    ######################
    vary_physical = {
        "setTemperature": cp.Uniform(300.0 * 0.85, 300.0 * 1.15),
        "time_factor_eq": cp.Uniform(600.0 * 0.85, 600.0 * 1.15),
        "BerendsenPressureTarget": cp.Uniform(1.01325 * 0.85, 1.01325 * 1.15),
        "time_sim1": cp.Uniform(1000.0 * 0.85, 1000.0 * 1.15),
    }
    vary_solver = {
        "box_size": cp.Uniform(14.0 * 0.85, 14.0 * 1.15),
        "cutoff": cp.Uniform(12.0 * 0.85, 12.0 * 1.15),
        "timestep": cp.Uniform(2.0 * 0.85, 2.0 * 1.15),
        "rigidtolerance": cp.Uniform(0.00001 * 0.85, 0.00001 * 1.15),
        "PMEGridSpacing": cp.Uniform(1.0 * 0.85, 1.0 * 1.15),
        "initTemperature_eq1": cp.Uniform(50.0 * 0.85, 50.0 * 1.15),
        "reassignIncr_eq1": cp.Uniform(1.0 * 0.85, 1.0 * 1.15),
        "langevinDamping": cp.Uniform(5.0 * 0.85, 5.0 * 1.15),
        "BerendsenPressureCompressibility": cp.Uniform(0.0000457 * 0.85,
                                                       0.0000457 * 1.15),
        "BerendsenPressureRelaxationTime": cp.Uniform(100.0 * 0.85,
                                                      100.0 * 1.15),
    }
    vary_discrete = {
        "switching": cp.DiscreteUniform(0, 1),  # ["off", "on"]
        "rigidBonds": cp.DiscreteUniform(0, 2),  # ["none", "water", "all"]
        "rigidIterations": cp.DiscreteUniform(int(math.floor(100 * 0.85)),
                                              int(math.ceil(100 * 1.15))),
        "nonbondedFreq": cp.DiscreteUniform(0, 2),
        "fullElectFrequency": cp.DiscreteUniform(1, 3),
        "stepspercycle": cp.DiscreteUniform(8, 12),
        "minimize_eq0": cp.DiscreteUniform(int(1000 * 0.85),
                                           int(1000 * 1.15)),
        "reassignFreq_eq1": cp.DiscreteUniform(int(100 * 0.85),
                                               int(100 * 1.15)),
        "langevinHydrogen": cp.DiscreteUniform(0, 1),  # ["no", "yes"]
        "useGroupPressure": cp.DiscreteUniform(0, 1),  # ["no", "yes"]
        "BerendsenPressureFreq": cp.DiscreteUniform(1, 3),
    }
    vary = {}
    vary.update(vary_physical)
    vary.update(vary_solver)

    ####################
    # create Sampler #
    ####################
    if campaign_config['sampler_name'] == 'SCSampler':
        sampler = uq.sampling.SCSampler(
            vary=vary,
            polynomial_order=campaign_config['polynomial_order'],
            quadrature_rule=campaign_config['quadrature_rule'],
            growth=campaign_config['growth'],
            sparse=campaign_config['sparse'],
            midpoint_level1=campaign_config['midpoint_level1'],
            dimension_adaptive=campaign_config['dimension_adaptive']
        )
    elif campaign_config['sampler_name'] == 'PCESampler':
        sampler = uq.sampling.PCESampler(
            vary=vary,
            polynomial_order=polynomial_order,
            rule=campaign_config['quadrature_rule'],
            sparse=campaign_config['sparse'],
            growth=campaign_config['growth']
        )
    # TODO: add other sampler here

    ###########################################
    # Associate the sampler with the campaign #
    ###########################################
    campaign.set_sampler(sampler)

    #########################################
    # draw all of the finite set of samples #
    #########################################
    campaign.draw_samples()
    run_ids = campaign.populate_runs_dir()

    ###################################
    # save campaign and sampler state #
    ###################################
    campaign.save_state(os.path.join(campaign_work_dir,
                                     "campaign_state.json")
                        )
    sampler.save_state(os.path.join(campaign_work_dir,
                                    "namd_sampler_state.0.pickle")
                       )

    backup_campaign_files(campaign_work_dir)


def load_campaign_config():
    '''
        loading user input sampler yaml file
    '''
    user_campaign_config_yaml_file = os.path.join(campaign_config_dir,
                                                  'campaign_config.yml')
    campaign_config = yaml.load(open(user_campaign_config_yaml_file),
                                Loader=yaml.SafeLoader
                                )
    campaign_config['params'] = json.load(
        open(
            os.path.join(campaign_config_dir,
                         'templates',
                         campaign_config['app_name'],
                         'params.json'
                         )
        )
    )

    campaign_config['campaign_name'] += '-' + campaign_config['sampler_name']

    # save campaign parameters in to a log file
    with open('campaign_config.log', 'w') as param_log:
        param_log.write('-' * 45 + '\n')
        param_log.write(" The used parameters for easyvvuq campaign\n")
        param_log.write('-' * 45 + '\n')
        yaml.dump(campaign_config, param_log, default_flow_style=False,
                  indent=4)
        param_log.write('-' * 45 + '\n\n')
    '''
    # print to campaign_config.log
    print("\ncampaign_config.log :")
    with open('campaign_config.log', 'r') as param_log:
        lines = param_log.readlines()
        print('\n'.join([line.rstrip() for line in lines]))
    '''
    return campaign_config


def backup_campaign_files(campaign_work_dir):

    backup_dir = os.path.join(campaign_work_dir, 'backup')

    # delete backup folder
    if os.path.exists(backup_dir):
        rmtree(backup_dir)
    os.mkdir(backup_dir)

    os.system(
        "rsync -pthrvz \
            --include='*.db' \
            --include='*.pickle' \
            --include='*.json' \
            --exclude='*' \
            {}/  {} ".format(campaign_work_dir, backup_dir)
    )


if __name__ == "__main__":
    init_campaign()
