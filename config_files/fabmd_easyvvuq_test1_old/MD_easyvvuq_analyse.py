#
# This file contains easyvvuq definitions specific for FabMD plugin.
# author: Hamid Arabnejad
#
import os
import yaml
import ruamel.yaml
import easyvvuq as uq
import json
from pprint import pprint
from sqlalchemy import create_engine
from MD_easyvvuq_init import load_campaign_params


work_dir = os.path.join(os.path.dirname(__file__))
sampler_inputs_dir = os.path.join(work_dir, 'sampler_inputs')


def analyse_campaign():

    campaign_params = load_campaign_params()

    # set campaign_work_dir
    campaign_work_dir = os.path.join(
        work_dir,
        'MD_easyvvuq_%s' % (campaign_params['sampler_name'])
    )

    for output_column in campaign_params['decoder_output_columns']:
        load_campaign_files(campaign_work_dir)
        print("output_column = %s" % (output_column))

        # reload Campaign
        print("=" * 45)
        print('Reloading campaign.db file')
        campaign = uq.Campaign(state_file=os.path.join(campaign_work_dir,
                                                       "campaign_state.json"),
                               work_dir=campaign_work_dir
                               )
        print('campaign %s reloaded ...' % (campaign._campaign_dir))
        print("Done ...")
        print("=" * 45)

        # in parts 1,2, and 3, since that we may need to have analyse for more
        # than 1 output column, so I modify the campaign.db file and then do
        # the analyse part with updated output column :)

        # part 1- read json file
        with open(os.path.join(campaign_work_dir,
                               "campaign_state.json"
                               ), "r") as infile:
            json_data = json.load(infile)

        # part 2- updating db file
        engine = create_engine(json_data['db_location'])
        with engine.connect() as con:
            sql_cmd = "UPDATE app "
            sql_cmd += "SET output_decoder = " \
                "JSON_SET(output_decoder,'$.state.output_columns[0]','%s')" \
                % (output_column)
            result = con.execute(sql_cmd)
            result.close()

        # part 3- we have to reload again campaign, I don't know why !!!
        campaign = uq.Campaign(state_file=os.path.join(campaign_work_dir,
                                                       "campaign_state.json"),
                               work_dir=campaign_work_dir
                               )

        sampler = campaign.get_active_sampler()
        campaign.set_sampler(sampler)
        campaign.collate()

        # Return dataframe containing all collated results
        collation_result = campaign.get_collation_result()

        # save results as csv
        collation_result.to_csv(os.path.join(campaign_work_dir,
                                             'collation_result_%s.csv' % (
                                                 output_column)
                                             ),
                                index=False
                                )
        print('campaign.get_collation_result :')
        pprint(collation_result)
        print("\n")

        # Post-processing analysis
        if campaign_params['sampler_name'] == 'SCSampler':
            analysis = uq.analysis.SCAnalysis(
                sampler=campaign._active_sampler,
                qoi_cols=[output_column]
            )
        elif campaign_params['sampler_name'] == 'PCESampler':
            analysis = uq.analysis.PCEAnalysis(
                sampler=campaign._active_sampler,
                qoi_cols=[output_column]
            )
        else:
            print("uq.analysis for sampler_name = %s is not specified! " %
                  (campaign_params['sampler_name']))
            exit(1)

        campaign.apply_analysis(analysis)
        results = campaign.get_last_analysis()

        mean = results.raw_data["statistical_moments"][output_column]["mean"]
        std = results.raw_data["statistical_moments"][output_column]["std"]
        var = results.raw_data["statistical_moments"][output_column]["var"]

        msg = []
        msg.append('statistical_moments:')
        msg.append('mean : %f' % (mean))
        msg.append('std  : %f' % (std))
        msg.append('var  : %f' % (var))
        print_msg_box('\n'.join(s for s in msg),
                      title='easyvvuq analysis for output_column = %s' %
                      (output_column))


def load_campaign_files(campaign_work_dir):

    backup_dir = os.path.join(campaign_work_dir, 'backup')
    os.system((
        "rsync -av -m  \
            --include='*.db' \
            --include='*.pickle' \
            --include='*.json' \
            --exclude='*' \
            {}/  {} ".format(backup_dir, campaign_work_dir)
    ))


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


if __name__ == "__main__":
    analyse_campaign()
