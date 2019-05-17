import os
import sys
from pprint import pprint
import easyvvuq as uq

plugin_path = get_plugin_path("FabMD")

@task
def fabmd_easyvvuq_example(config, **args):
    update_environment(args)
    with_config(config)

    # need a tmp folder for EasyVVUQ
    tmp_path = plugin_path+"/tmp"
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)

    #env.config_path

    # Input file containing information about parameters of interest
    input_json = "ensemble_input.json"

    # 1. Initialize `Campaign` object which information on parameters to be sampled
    #    and the values used for all sampling runs
    my_campaign = uq.Campaign(state_filename=input_json, workdir=tmp_path)

    # 2. Set which parameters we wish to include in the analysis and the
    #    distribution from which to draw samples
    my_campaign.vary_param("velocity_seed", dist=uq.distributions.uniform_integer(1,1000000))

    # 3. Determine the runs to be executed in order to sample the parameter space.
    #    Settings for the chosen number of runs are produced using `Sampler`s
    #    which determine how combinations of parameters are selected for each one

    # First we create three samples where the varying parameter ()"mu", the mean)
    # is chosen directly from the selected distribution. If multiple parameters
    # were allowed to vary then all would be sampled independently.
    number_of_samples = 5
    random_sampler = uq.elements.sampling.RandomSampler(my_campaign)
    my_campaign.add_runs(random_sampler, max_num=number_of_samples)

    # The `Replicate` sampler creates copies of the different parameter runs
    # created above (to gain additional sampled in the same area of parameter
    # space).
    #number_of_replicas = 1
    #replicator = uq.elements.sampling.Replicate(my_campaign,
    #                                        replicates=number_of_replicas)
    #my_campaign.add_runs(replicator)

    # 4. Create directories containing inputs for each run containing the
    #    parameters determined by the `Sampler`(s).
    #    This makes use of the `Encoder` specified in the input file.
    my_campaign.populate_runs_dir()
"""
# 5. Run execution - note this method of running all jobs is just for demo
#    purposes.
my_campaign.apply_for_each_run_dir(
        uq.actions.ExecuteLocal("gauss.py gauss_in.json"))

# 6. Aggregate the results from all runs.
#    This makes use of the `Decoder` selected in the input file to interpret the
#    run output and produce data that can be integrated in a summary pandas
#    dataframe.

output_filename = my_campaign.params_info['out_file']['default']
output_columns = ['Value']

aggregate = uq.elements.collate.AggregateSamples(
                                                my_campaign,
                                                output_filename=output_filename,
                                                output_columns=output_columns,
                                                header=0,
                                                average=True
                                                )
aggregate.apply()

# 7. Run analysis - in this case generate bootstrap estimate of the mean and
#    accompanying error bars.
ensemble_boot = uq.elements.analysis.EnsembleBoot(my_campaign)
results, output_file = ensemble_boot.apply()

# These lines output the analysed data and a log of the steps performed.
pprint(results)

pprint(my_campaign.log)

# The saved state of the `Campaign` contains the state of all runs and can be
# loaded to perform further sampling or analysis.
my_campaign.save_state('final_state.json')
"""

