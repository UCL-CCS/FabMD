#
# This file contains easyvvuq definitions specific for FabMD plugin.
# author: Hamid Arabnejad
#
import os
import yaml
import ruamel.yaml
from pprint import pprint
from shutil import rmtree
import json
import chaospy as cp
import numpy as np
import tempfile
import easyvvuq as uq

# there imports are required for my customized Campaign easyvvuq class
from easyvvuq.constants import default_campaign_prefix, Status
from easyvvuq.db.sql import CampaignDB
from easyvvuq.data_structs import CampaignInfo
from easyvvuq import Campaign
from easyvvuq.analysis import SCAnalysis
from easyvvuq.encoders import GenericEncoder

work_dir = os.path.join(os.path.dirname(__file__))
sampler_inputs_dir = os.path.join(work_dir, 'sampler_inputs')


def init_campaign():

    campaign_params = load_campaign_params()

    # set campaign_work_dir
    campaign_work_dir = os.path.join(
        work_dir,
        'MD_easyvvuq_%s' % (campaign_params['sampler_name'])
    )
    # delete campaign_work_dir is exists
    if os.path.exists(campaign_work_dir):
        rmtree(campaign_work_dir)
    os.mkdir(campaign_work_dir)

    # ------------------------------------------------------
    # here, I used a customized version of Campaign class to
    # better arrangements of generated files and folders
    # ------------------------------------------------------
    uq.Campaign = CustomCampaign

    # Set up a fresh campaign
    campaign = uq.Campaign(name=campaign_params['campaign_name'],
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
        output_columns=campaign_params['decoder_output_columns'],
        header=0
    )

    # Create a collation element for this campaign
    collater = uq.collate.AggregateSamples(average=False)

    # Add the covid19-SCSampler app
    campaign.add_app(name=campaign_params['campaign_name'],
                     params=campaign_params['params'],
                     encoder=encoder,
                     decoder=decoder,
                     collater=collater)

    # parameters to vary
    vary = {}
    for param in campaign_params['selected_parameters']:
        lower_value = campaign_params['parameters'][param]['uniform_range'][0]
        upper_value = campaign_params['parameters'][param]['uniform_range'][1]
        if campaign_params['distribution_type'] == 'DiscreteUniform':
            vary.update({param: cp.DiscreteUniform(lower_value, upper_value)})
        elif campaign_params['distribution_type'] == 'Uniform':
            vary.update({param: cp.Uniform(lower_value, upper_value)})

    # create SCSampler
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
    campaign.set_sampler(sampler)

    # Will draw all (of the finite set of samples)
    campaign.draw_samples()

    run_ids = campaign.populate_runs_dir()

    # save campaign and sampler state
    campaign.save_state(os.path.join(campaign_work_dir,
                                     "campaign_state.json"
                                     )
                        )

    print("=" * 45)
    print("With user's specified parameters for sampler")
    print("easyvvuq generates %d runs" % (len(run_ids)))
    print("=" * 45)

    backup_campaign_files(campaign_work_dir)


def load_campaign_params():
    '''
        loading user input sampler yaml file
    '''
    user_campaign_params_yaml_file = os.path.join(sampler_inputs_dir,
                                                  'campaign_params.yml')
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


class CustomCampaign(Campaign):
    # ----------------------------------------------------------------------
    # changes :
    # send runs_dir='SWEEP' when we call CampaignInfo
    # change location of campaign.db to work directory
    # ----------------------------------------------------------------------

    def init_fresh(self, name, db_type='sql',
                   db_location=None, work_dir='.'):

        # Create temp dir for campaign
        campaign_prefix = default_campaign_prefix
        if name is not None:
            campaign_prefix = name

        campaign_dir = tempfile.mkdtemp(prefix=campaign_prefix, dir=work_dir)

        self._campaign_dir = os.path.relpath(campaign_dir, start=work_dir)

        self.db_location = db_location
        self.db_type = db_type

        if self.db_type == 'sql':
            from easyvvuq.db.sql import CampaignDB
            if self.db_location is None:
                self.db_location = "sqlite:///" + work_dir + "/campaign.db"
                # self.db_location = "sqlite:///" + self.campaign_dir +
                # "/campaign.db"
        else:
            message = (f"Invalid 'db_type' {db_type}. Supported types are "
                       f"'sql'.")
            logger.critical(message)
            raise RuntimeError(message)
        from easyvvuq import __version__
        info = CampaignInfo(
            name=name,
            campaign_dir_prefix=default_campaign_prefix,
            easyvvuq_version=__version__,
            campaign_dir=self.campaign_dir,
            # runs_dir=os.path.join(campaign_dir, 'runs')
            runs_dir=os.path.join(campaign_dir, 'SWEEP')
        )
        self.campaign_db = CampaignDB(location=self.db_location,
                                      new_campaign=True,
                                      name=name, info=info)

        # Record the campaign's name and its associated ID in the database
        self.campaign_name = name
        self.campaign_id = self.campaign_db.get_campaign_id(self.campaign_name)

    # ----------------------------------------------------------------------
    # changes :
    # return generated run_ids when we call populate_runs_dir
    # ----------------------------------------------------------------------

    def populate_runs_dir(self):

        # Get the encoder for this app. If none is set, only the directory
        # structure will be created.
        active_encoder = self._active_app_encoder
        if active_encoder is None:
            logger.warning(
                'No encoder set for this app. Creating directory structure only.')

        run_ids = []

        for run_id, run_data in self.campaign_db.runs(
                status=Status.NEW, app_id=self._active_app['id']):

            # Make directory for this run's output
            os.makedirs(run_data['run_dir'])

            # Encode run
            if active_encoder is not None:
                active_encoder.encode(params=run_data['params'],
                                      target_dir=run_data['run_dir'])

            run_ids.append(run_id)
        self.campaign_db.set_run_statuses(run_ids, Status.ENCODED)
        return run_ids


if __name__ == "__main__":
    init_campaign()
