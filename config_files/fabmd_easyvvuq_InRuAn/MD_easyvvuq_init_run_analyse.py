#
# This file contains easyvvuq definitions specific for FabMD plugin.
# author: Hamid Arabnejad
#
import os
import yaml
# import ruamel.yaml
# from pprint import pprint
from shutil import rmtree
# import json
import chaospy as cp
import numpy as np
# import tempfile
import easyvvuq as uq
import time
# there imports are required for my customized Campaign easyvvuq class
from easyvvuq.constants import default_campaign_prefix, Status
from easyvvuq.db.sql import CampaignDB
from easyvvuq.data_structs import CampaignInfo
from easyvvuq import Campaign
from easyvvuq.analysis import SCAnalysis
from easyvvuq.encoders import GenericEncoder
# try:
#     from fabsim.base import *
# except ImportError:
#     from fabsim.base import *

# How to configure and run easyvvuq with FabMD
# bash Anaconda3-5.2.0-Linux-x86_64.sh
# Logout
# login
# conda   <-- check if it can recognize
# pip3 install easyvvuq
# pip3 install --upgrade requests



import sys
# $lammps_args  $lammps_input  $machine_name   $run_command

def init_run_analyse_campaign(work_dir=None, sampler_inputs_dir=None , inpt=None):

    print('inpt', inpt)
    # from shlex import quote

    machine_name = inpt[0]
    run_command = inpt[1]
    lammps_exec = inpt[2]
    lammps_args = inpt[3]
    # inpt= ' '.join(quote(arg) for arg in inpt)

    campaign_params = load_campaign_params(sampler_inputs_dir=sampler_inputs_dir)
    keys = list(campaign_params.keys())
    CRED = '\33[31m'
    CEND = '\33[0m'
    print('Campaign parameters <---------->')
    for key in keys:
        print(CRED + key, ':' + CEND, campaign_params[key])
    print('\x1b[6;30;45m' + '                   ' + '\x1b[0m')
    # print('Campaign_params:', campaign_params)
    # set campaign_work_dir
    campaign_work_dir = os.path.join(
        work_dir,
        'MD_easyvvuq_%s' % (campaign_params['sampler_name'])
    )
    # delete campaign_work_dir is exists
    if os.path.exists(campaign_work_dir):
        rmtree(campaign_work_dir)
    os.mkdir(campaign_work_dir)

    db_location = "sqlite:///" + campaign_work_dir + "/campaign.db"

    # ------------------------------------------------------
    # here, I used a customized version of Campaign class to
    # better arrangements of generated files and folders
    # ------------------------------------------------------
    # uq.Campaign = CustomCampaign

    # Set up a fresh campaign
    campaign = uq.Campaign(name=campaign_params['campaign_name'], db_location=db_location,
                           work_dir=campaign_work_dir)

    # Create an encoder and decoder
    encoder = uq.encoders.GenericEncoder(
        template_fname=os.path.join(sampler_inputs_dir, campaign_params[
                                    'encoder_template_fname']),
        delimiter=campaign_params['encoder_delimiter'],
        target_filename=campaign_params['encoder_target_filename']
    )

    decoder = uq.decoders.SimpleCSV(
        target_filename=campaign_params['decoder_target_filename'],
        output_columns=campaign_params['decoder_output_columns']
    )
    # execute = uq.actions.ExecuteLocal(
    #     "python3 {}/cooling_model.py cooling_in.json".format(work_dir)
    # )
    host = 'localhost'
    # execute = uq.actions.ExecuteLocal(
    #     "fabsim  {}  lammps_run_campaign:fabmd_easyvvuq_test1, lammps_input={}".format(host, campaign_params['encoder_target_filename'])
    # )
    # execute = uq.actions.ExecuteLocal(
    #     "fabsim  {}  lammps_run_campaign:fabmd_easyvvuq_test1".format(host)
    # )
    this_path = campaign._campaign_dir

    # machine_name = "'" + str(machine_name) + "'"
    # run_command = "'" + str(run_command) + "'"
    # lammps_exec = "'" + str(lammps_exec) + "'"
    # lammps_args = "'" + str(lammps_args) + "'"
    print('machine name:', CRED + str(machine_name) + CEND)
    print('run command:', CRED + str(run_command) + CEND)
    print('lammps exec:', CRED + str(lammps_exec) + CEND)
    print('lammps args:', CRED + str(lammps_args) + CEND)
    print('work_dir:', CRED + str(os.getcwd()) + CEND)
    # execute = uq.actions.ExecuteLocal(
    #     'python3 {}/easyvvuq_MD_RUN.py {} {} {} {} {} {} '.format(work_dir,
    #     campaign_params['encoder_target_filename'], this_path, machine_name, run_command, lammps_exec, lammps_args)
    # )
    if str(machine_name) == 'localhost':
        print('\x1b[6;30;45m' + '.........................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'running on local machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '.........................' + '\x1b[0m')
        execute = uq.actions.ExecuteLocal(
            'python3 {}/easyvvuq_MD_RUN_localhost.py {} {} {}'.format(os.getcwd(),
            campaign_params['encoder_target_filename'], this_path, inpt))
    else:
        print('\x1b[6;30;45m' + '..........................' + '\x1b[0m')
        print('\x1b[6;30;45m' + 'running on remote machine!' + '\x1b[0m')
        print('\x1b[6;30;45m' + '..........................' + '\x1b[0m')
        execute = uq.actions.ExecuteLocal(
            'python3 {}/easyvvuq_MD_RUN_remote.py {} {} {}'.format(os.getcwd(),
            campaign_params['encoder_target_filename'], this_path, inpt))

    actions = uq.actions.Actions(
        uq.actions.CreateRunDirectory(root=campaign_work_dir, flatten=True),
        uq.actions.Encode(encoder),
        execute,
        uq.actions.Decode(decoder))

    # # Create a collation element for this campaign
    # # collater = uq.collate.AggregateSamples(average=False)
    # campaign.add_app(
    #     name="cooling",
    #     params=params,
    #     actions=actions
    # )
    #
    # # Create the sampler
    # vary = {
    #     "kappa": cp.Uniform(0.025, 0.075),
    #     "t_env": cp.Uniform(15, 25)
    # }
    # sampler = uq.sampling.PCESampler(vary=vary, polynomial_order=3)
    #
    # # Associate the sampler with the campaign
    # campaign.set_sampler(sampler)
    #
    # # Run the cases
    # campaign.execute(pool=client).collate()
    # Add the covid19-SCSampler app
    print('campaign_params[params]', campaign_params['params'])
    campaign.add_app(
        name=campaign_params['campaign_name'],
        params=campaign_params['params'],
        actions=actions
    )
    # campaign.add_app(name=campaign_params['campaign_name'],
    #                  params=campaign_params['params'],
    #                  encoder=encoder,
    #                  decoder=decoder)

    # parameters to vary
    vary = {}
    for param in campaign_params['selected_parameters']:
        lower_value = campaign_params['parameters'][param]['uniform_range'][0]
        upper_value = campaign_params['parameters'][param]['uniform_range'][1]
        if campaign_params['distribution_type'] == 'DiscreteUniform':
            vary.update({param: cp.DiscreteUniform(lower_value, upper_value)})
        elif campaign_params['distribution_type'] == 'Uniform':
            vary.update({param: cp.Uniform(lower_value, upper_value)})

    # # create SCSampler
    print('vary', vary)
    if campaign_params['sampler_name'] == 'SCSampler':
        sampler = uq.sampling.SCSampler(
            vary=vary,
            polynomial_order=campaign_params['polynomial_order'],
            quadrature_rule=campaign_params['quadrature_rule'],
            growth=campaign_params['growth'],
            sparse=campaign_params['sparse'],
            midpoint_level1=campaign_params['midpoint_level1'],
            dimension_adaptive=campaign_params['dimension_adaptive']
        )
    elif campaign_params['sampler_name'] == 'PCESampler':
        sampler = uq.sampling.PCESampler(
            vary=vary,
            polynomial_order=campaign_params['polynomial_order'],
            rule=campaign_params['quadrature_rule'],
            sparse=campaign_params['sparse'],
            growth=campaign_params['growth']
        )
    elif campaign_params['sampler_name'] == 'QMCSampler':
        sampler = uq.sampling.QMCSampler(
            vary=vary,
            n_mc_samples=32,
            count=2
        )
    elif campaign_params['sampler_name'] == 'RandomSampler':
        # TODO:	ask about this error from easyvvuq dev team
        # 		for some reasons, RandomSampler gives me this RuntimeError
        # 		RuntimeError: Sampling_element 'random_sampler' is an infinite
        # 		generator, therefore a finite number of draws (n > 0)
        #  		must be specified.
        sampler = uq.sampling.RandomSampler(
            vary=vary
        )

    # Associate the sampler with the campaign
    # sampler=uq.sampling.MCSampler(vary=vary, n_mc_samples=16)
    campaign.set_sampler(sampler)
    time_start = time.time()
    campaign.draw_samples()
    print("Number of samples = %s" % campaign.get_active_sampler().count)
    #
    time_end = time.time()
    from dask.distributed import Client
    client = Client(processes=True, threads_per_worker=1)
    print("Time for phase 2 = %.3f" % (time_end - time_start))
    time_start = time.time()
    campaign.execute(pool=client).collate()
    # campaign.set_sampler(sampler)
    #
    # campaign.execute(nsamples=5).collate()

    time_end = time.time()
    print("Time for phase 3 = %.3f" % (time_end - time_start))
    time_start = time.time()
    # client.close()
    # client.shutdown()
    time_end = time.time()
    print("Time for phase 4 = %.3f" % (time_end - time_start))
    time_start = time.time()
    output_column = campaign_params['decoder_output_columns']
    # results_df = campaign.get_collation_result()
    # Post-processing analysis
    if campaign_params['sampler_name'] == 'SCSampler':
        analysis = uq.analysis.SCAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["solvation_energy"]
        )
    elif campaign_params['sampler_name'] == 'PCESampler':
        analysis = uq.analysis.PCEAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["solvation_energy"]
        )
    elif campaign_params['sampler_name'] == 'QMCSampler':
        analysis = uq.analysis.QMCAnalysis(
            sampler=campaign._active_sampler,
            qoi_cols=["solvation_energy"]
        )


    else:
        print("uq.analysis for sampler_name = %s is not specified! " %
              (campaign_params['sampler_name']))
        exit(1)
    time_end = time.time()
    print("Time for phase 5 = %.3f" % (time_end - time_start))
    time_start = time.time()
    # campaign.apply_analysis(
    #     uq.analysis.GaussianProcessSurrogate(
    #         sampler=campaign.get_active_sampler(),
    #         # qoi_cols=["te", "ne", "rho", "rho_norm"]
    #         qoi_cols=[output_column]
    #
    #     )
    # )
    # campaign.apply_analysis(
    #         uq.analysis.SCAnalysis(
    #             sampler=campaign.get_active_sampler(),
    #             qoi_cols=[output_column]
    #         )
    # )
    campaign.apply_analysis(analysis)

    time_end = time.time()
    print("Time for phase 6 = %.3f" % (time_end - time_start))
    time_start = time.time()

    results = campaign.get_last_analysis()


    mean = results.describe("solvation_energy","mean")
    std = results.describe("solvation_energy", "std")
    var = results.describe("solvation_energy", "var")

    time_end = time.time()

    print("Time for phase 7 = %.3f" % (time_end - time_start))
    time_start = time.time()
    print('mean', mean)
    print('std', std)
    print('var', var)
    mean = np.mean(mean)
    std = np.mean(std)
    var = np.mean(var)
    msg = []
    msg.append('statistical_moments:')
    msg.append('mean : %f' % (mean))
    msg.append('std  : %f' % (std))
    msg.append('var  : %f' % (var))
    print_msg_box('\n'.join(s for s in msg),
                  title='easyvvuq analysis for output_column = %s' %
                        (output_column))
    # results = campaign.analyse(qoi_cols=["te"])
    #
    # run_ids = campaign.populate_runs_dir()
    #
    # # save campaign and sampler state
    # campaign.save_state(os.path.join(campaign_work_dir,
    #                                  "campaign_state.json"
    #                                  )
    #                     )

    # print("=" * 45)
    # print("With user's specified parameters for sampler")
    # print("easyvvuq generates %d runs" % (len(run_ids)))
    # print("=" * 45)
    #
    # backup_campaign_files(campaign_work_dir)
def print_msg_box(msg, indent=1, width=None, title=None, border="═"):
    """
        Print message-box with optional title.
        source : https://stackoverflow.com/questions/39969064/how-to-print-a-message-box-in-python
    """
    if len(msg) == 0:
        return

    if border == "═":
        t_l, t_r, b_l, b_r = "╔", "╗", "╚", "╝"
        l = r = "║"
        t = b = "═"

    elif border == "-":
        t_l, t_r, b_l, b_r = "┌", "┐", "└", "┘"
        l = r = "|"
        t = b = "─"
    lines = msg.split('\n')

    space = " " * indent
    if not width:
        width = max(max(map(len, lines)), len(title))
    box = f'{t_l}{t * (width + indent * 2)}{t_r}\n'  # upper_border
    if title:
        box += f'{l}{space}{title:<{width}}{space}{r}\n'  # title
        # underscore
        box += f'{l}{space}{"-" * len(title):<{width}}{space}{r}\n'
    box += ''.join([f'{l}{space}{line:<{width}}{space}{r}\n' for line in lines])
    box += f'{b_l}{b * (width + indent * 2)}{b_r}'  # lower_border
    print(box)

def load_campaign_params(sampler_inputs_dir=None):
    '''
        loading user input sampler yaml file
    '''
    user_campaign_params_yaml_file = os.path.join('campaign_params.yml')
    campaign_params = yaml.load(open(user_campaign_params_yaml_file),
                                Loader=yaml.SafeLoader
                                )
    campaign_params['campaign_name'] += '-' + campaign_params['sampler_name']

    # save campaign parameters in to a log file
    with open('campaign_params.log', 'w') as param_log:
        param_log.write('-' * 45 + '\n')
        param_log.write(" The used parameters for easyvvuq campaign\n")
        param_log.write('-' * 45 + '\n')
        yaml.dump(campaign_params, param_log, default_flow_style=False,
                  indent=4)
        param_log.write('-' * 45 + '\n\n')

    # print to campaign_params.log
    print("\ncampaign_params.log :")
    with open('campaign_params.log', 'r') as param_log:
        lines = param_log.readlines()
        print('\n'.join([line.rstrip() for line in lines]))
        return campaign_params


def backup_campaign_files(campaign_work_dir):

    backup_dir = os.path.join(campaign_work_dir, 'backup')

    # delete backup folder
    if os.path.exists(backup_dir):
        rmtree(backup_dir)
    os.mkdir(backup_dir)

    os.system(
        "rsync -av -m -v \
            --include='*.db' \
            --include='*.pickle' \
            --include='*.json' \
            --exclude='*' \
            {}/  {} ".format(campaign_work_dir, backup_dir)
    )




if __name__ == "__main__":
    # CRED = '\33[31m'
    # CEND = '\33[0m'
    # $machine_name    '$run_command'   $lammps_exec   '$lammps_args'

    # machine_name = sys.argv[1]
    # run_command1 = sys.argv[2]
    # run_command2 = sys.argv[3]
    # run_command3 = sys.argv[4]
    # lammps_exec = sys.argv[5]
    # lammps_args = " ".join(sys.argv[6:])
    # print('machine name:', CRED + str(machine_name) + CEND)
    # print('run command:', CRED + str(run_command1) + CEND)
    # print('number process(np) arg:', CRED + str(run_command2) + CEND)
    # print('number cores:', CRED + str(run_command3) + CEND)
    # print('lammps exec:', CRED + str(lammps_exec) + CEND)
    # print('lammps args:', CRED + str(lammps_args) + CEND)


    # machine_name = sys.argv[1]
    # run_command = sys.argv[2]
    # lammps_exec = sys.argv[3]
    # lammps_args = sys.argv[4]
    inpt = []
    # inpt.append("'" + sys.argv[1] + "'")
    # inpt.append("'" + sys.argv[2] + "'")
    # inpt.append("'" + sys.argv[3] + "'")
    # inpt.append("'" + sys.argv[4] + "'")
    inpt.append(sys.argv[1])
    inpt.append(sys.argv[2])
    inpt.append(sys.argv[3])
    inpt.append(sys.argv[4])

    # " ".join(map(shlex.quote, sys.argv[1:]))
    # print('machine name:', CRED + str(machine_name) + CEND)
    # print('run command:', CRED + str(run_command) + CEND)
    # print('lammps exec:', CRED + str(lammps_exec) + CEND)
    # print('lammps args:', CRED + str(lammps_args) + CEND)



    work_dir1 = os.path.join(os.path.dirname(__file__))
    from pathlib import Path
    # se = os.listdir('../../../..')
    # for path in se:
    #     full_path = os.path.join(d, path)
    #     if os.path.isfile(full_path):
    #         print(full_path)
    # full_path = os.path.join(se['plugins'], '/plugins/FabMD')
    # p = Path(__file__).parents[4]
    #
    # print('FabSim3 path:', p)
    sampler_inputs_dir = os.path.join(work_dir1)
    # # FabMD_path = str(se)
    # full_path = str(p) + '/plugins/FabMD/machines_FabMD_user.yml'
    # # full_path = 'r' + str(full_path)
    # print('FabMD_path:', full_path)
    # with open(full_path, 'r') as file:
    #     documents = yaml.full_load(file)
    #     for item, doc in documents.items():
    #         print(item, ":", doc)
    # defaults = yaml.load(open(full_path + '/machines_FabMD_user.yml'), 'lammps_exec')
    # print('defaults:', defaults)
    init_run_analyse_campaign(work_dir=work_dir1, sampler_inputs_dir=sampler_inputs_dir, inpt=inpt)
