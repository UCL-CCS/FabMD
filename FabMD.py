# -*- coding: utf-8 -*-
#
# This source file is part of the FabSim software toolkit, which is
# distributed under the BSD 3-Clause license.
# Please refer to LICENSE for detailed information regarding the licensing.
#
# This file contains FabSim definitions specific to FabNanoMD.

from base.fab import *

# from plugins.FabMD.user_workflows import *

# Add local script, blackbox and template path.
add_local_paths("FabMD")

FabMD_path = get_plugin_path('FabMD')


@task
def lammps(config, **args):
    md_job(config, 'lammps', **args)


@task
def gromacs(config, **args):
    env.grompp_command = make_grompp_command(config, **args)
    md_job(config, 'gromacs', **args)


def md_job(config, script, **args):
    """Submit an MD job to the remote queue with a given script; e.g. LAMMPS
    The job results will be stored with a name pattern as defined in the
    environment, e.g. cylinder-abcd1234-legion-256
    config : config directory to use to define geometry, e.g. config=cylinder
    Keyword arguments:
            cores : number of compute cores to request
            images : number of images to take
            steering : steering session i.d.
            wall_time : wall-time job limit
            memory : memory per node
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


@task
def lammps_ensemble(config, sweep_dir=False, **kwargs):
    md_ensemble(config, 'lammps', sweep_dir, **kwargs)


@task
def gromacs_ensemble(config, sweep_dir=False, **kwargs):
    env.grompp_command = make_grompp_command(config, kwargs)
    md_ensemble(config, 'gromacs', sweep_dir, kwargs)


def md_ensemble(config, script, sweep_dir, **kwargs):
    defaults = yaml.load(open(FabMD_path+'/default_settings/'+script+'.yaml'))
    ensemble_args = dict(script=script,
                         wall_time=defaults['wall_time'],
                         lammps_input=defaults['lammps_input'],
                         cores=defaults['cores'],
                         memory='2G')
    # input_name_in_config='topology.data')
    ensemble_args.update(kwargs)

    # If sweep_dir not set assume it is a directory in config with default name
    if sweep_dir == False:
        path_to_config = find_config_file_path(config)
        sweep_dir = path_to_config + "/" + defaults["sweep_dir_name"]

    #if 'input_name_in_config' not in ensemble_args:
    #    raise RuntimeError(
    #        'Must declare input_name_in_config: the generic name which sweep'+
    #         'directory files will be changed to')

    run_ensemble(config, sweep_dir, **ensemble_args)


def make_grompp_command(config, args):
    config_dir = find_config_file_path(config)
    required_files = {'grompp': {'extension': '.mdp', 'flag': 'f'},
                      'conf': {'extension': '.gro', 'flag': 'c'},
                      'topol': {'extension': '.top', 'flag': 'p'}}
    optional_files = {'checkpoint': {'extension': '.cpt', 'flag': 't'},
                      'index': {'extension': '.ndx', 'flag': 'n'}}

    defaults = yaml.load(open(FabMD_path+'/default_settings/gromacs.yaml'))

    grompp_args = {}
    for reqfile in required_files:
        flag = required_files[reqfile]['flag']

        # specified in command line?
        if reqfile in args:
            grompp_args[flag] = args[reqfile]
            continue

        # specified as default?
        if reqfile in defaults['required_files']:
            if defaults['required_files'][reqfile]:
                grompp_args[flag] = defaults['required_files'][reqfile]
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
        # specified in command line?
        if optfile in args:
            grompp_args[flag] = args[optfile]
            continue

    grompp_command = ''
    for arg in grompp_args:
        grompp_command += '-'+arg+' '+grompp_args[arg]+' '
    print('grompp arguments = ', grompp_command)
    return grompp_command


@task
def lammps_epoxy(config, **args):
    """Submit a LAMMPS job to the remote queue.
    The job results will be stored with a name pattern as defined in the
    environment, e.g. cylinder-abcd1234-legion-256
    config : config directory to use to define geometry, e.g. config=cylinder
    Keyword arguments:
            cores : number of compute cores to request
            images : number of images to take
            steering : steering session i.d.
            wall_time : wall-time job limit
            memory : memory per node
    """

    for repl in range(1, 3):
        mat = "g0"
        temp = 300.0
        nts = 1
        dld = "x"
        gof = "flake"

        ddir = "./init.%s_%d.bin" % (mat, repl)
        odir = "./"

        env.lammps_args = " -var loco %s -var locd %s -var epoxy %s -var tempt %f -var nsstrain %d" \
                          " -var nrep %d -var dld %s -var gflake %s -screen none" \
            % (odir, ddir, mat, temp, nts, repl, dld, gof)

        lammps(config, **args)


# @task
# def lammps_swelling_test(config, **args):
    """Submits a set of LAMMPS jobs to the remote queue, as part of a clay swelling test."""

    # let's first try to run the exfoliated one.

    # lammps_in_file =

    # with_config(config)
    # execute(put_configs,config)

    # loop over swelling values

    #update_environment(dict(job_results, job_config_path))
    # job(dict(script='lammps',
    # cores=4, wall_time='0:15:0',memory='2G'),args)

### IBI ###


@task
def do_ibi(number, outdir, pressure=1, config_name="peg", copy="yes", ibi_script="ibi.sh", atom_dir=os.path.join(env.localroot, 'python')):
    """ Copy the obtained output to a work directory, do an IBI iteration and make a new config file from the resulting data. """
    ibi_in_dir = os.path.join(env.localroot, 'results', outdir)
    ibi_out_dir = os.path.join(
        env.localroot, 'output_blackbox', os.path.basename(ibi_script), outdir)
    ibi_script_dir = os.path.join(env.localroot, 'python')
    local("mkdir -p %s" % (ibi_out_dir))
#    if copy=="yes":
#      blackbox("copy_lammps_results.sh", "%s %s %d" % (os.path.join(env.localroot,'results',outdir), os.path.join(env.localroot,'python'), int(number)))
    blackbox(ibi_script, "%s %s %s %s %s" %
             (atom_dir, number, pressure, ibi_in_dir, ibi_out_dir))
    if copy == "yes":
        blackbox("prepare_lammps_config.sh", "%s %s %s %d %s" % (ibi_out_dir, os.path.join(
            env.localroot, 'config_files'), config_name, int(number)+1, atom_dir))


@task
@task
def do_pmf(number, outdir, atom_type1, atom_type2, config_name="peg", copy="yes", pmf_script="pmf.sh", atom_dir=os.path.join(env.localroot, 'python')):
    """ Copy the obtained output to a work directory, do an IBI iteration and make a new config file from the resulting data. """
    pmf_in_dir = os.path.join(env.localroot, 'results', outdir)
    pmf_out_dir = os.path.join(env.localroot, 'output_blackbox', outdir)
    #pmf_out_dir = os.path.join(env.localroot,'output_blackbox',os.path.basename(pmf_script),outdir)
    ibi_script_dir = os.path.join(env.localroot, 'python')
    local("mkdir -p %s" % (pmf_out_dir))
#    if copy=="yes":
#      blackbox("copy_lammps_results.sh", "%s %s %d" % (os.path.join(env.localroot,'results',outdir), os.path.join(env.localroot,'python'), int(number)))
    blackbox(pmf_script, "%s %s %s %s %s %s %s " % (atom_type1, atom_type2,
                                                    number, pmf_in_dir, pmf_out_dir, atom_dir, ibi_script_dir))
    if copy == "yes":
        blackbox("prepare_lammps_config_pmf.sh", "%s %s %s %d %s " % (pmf_out_dir, os.path.join(
            env.localroot, 'config_files'), config_name, int(number)+1, atom_dir))


@task
def ibi_analysis_multi(start_iter, num_iters, outdir_prefix, outdir_suffix, ibi_script="ibi.sh", pressure=1, atom_dir=os.path.join(env.localroot, 'python')):
    """ Recreate IBI analysis results based on the output files provided.
    Example use: fab hector ibi_analysis_multi:start_iter=7,num_iters=3,outdir_prefix=peg_,outdir_suffix=_hector_32 """
    si = int(start_iter)
    ni = int(num_iters)
    for i in xrange(si, si+ni):
        outdir = "%s%d%s" % (outdir_prefix, i, outdir_suffix)
        do_ibi(i, outdir, pressure, outdir_prefix, "no", ibi_script, atom_dir)

#        ibi_in_dir = os.path.join(env.localroot,'results',outdir)
#        ibi_out_dir = os.path.join(env.localroot,'ibi_output',outdir)
#        local("mkdir -p %s" % (ibi_out_dir))
#        blackbox("copy_lammps_results.sh", "%s %s %d" % (os.path.join(env.localroot,'results',"%s%d%s" % (outdir_prefix,i,outdir_suffix)), os.path.join(env.localroot,'python'), i))
#        blackbox(ibi_script, "%s %s %s %s" % (i, pressure, ibi_in_dir, ibi_out_dir))


@task
def full_ibi(config, number, outdir, config_name, pressure=0.3, ibi_script="ibi.sh", atom_dir=os.path.join(env.localroot, 'python'), **args):
    """ Performs both do_ibi and runs lammps with the newly created config file.
    Example use: fab hector full_ibi:config=2peg4,number=3,outdir=2peg3_hector_32,config_name=2peg,cores=32,wall_time=3:0:0 """
    do_ibi(number, outdir, pressure, config_name, "yes", ibi_script, atom_dir)
    lammps(config, **args)
    wait_complete()
    fetch_results(regex="*%s*" % (config_name))


@task
def full_pmf(config, number, outdir, config_name, atom_type1, atom_type2, pmf_script="pmf.sh", atom_dir=os.path.join(env.localroot, 'python'), **args):
    """ Performs both do_ibi and runs lammps with the newly created config file.
    Example use: fab hector full_ibi:config=2peg4,number=3,outdir=2peg3_hector_32,config_name=2peg,cores=32,wall_time=3:0:0 """
    print("Starting PMF script.")
    do_pmf(number, outdir, atom_type1, atom_type2,
           config_name, "yes", pmf_script, atom_dir)
    print("PMF script finished. Launching LAMMPS.")
    update_environment(args)
    env.lammps_args = "-partition %sx%s" % (int(env.cores)/int(
        env.cores_per_replica), int(env.cores_per_replica))
    lammps(config, **args)
    wait_complete()
    fetch_results(regex="*%s*" % (config_name))


@task
def full_ibi_multi(start_iter, num_iters, config_name, outdir_suffix, pressure=0.3, script="ibi.sh", atom_dir="default", **args):
    """ Do multiple IBI iterations in one command.
    Example use: fab hector full_ibi_multi:start_iter=7,num_iters=3,config_name=2peg,outdir_suffix=_hector_32,cores=32,wall_time=3:0:0 """

    if atom_dir == "default":
        atom_dir = os.path.join(env.localroot, "results",
                                "%s%d%s" % (config_name, 1, outdir_suffix))

    si = int(start_iter)
    ni = int(num_iters)

    pressure_changed = 0

    for i in xrange(si, si+ni):
        full_ibi("%s%d" % (config_name, i+1), i, "%s%d%s" % (config_name, i,
                                                             outdir_suffix), config_name, pressure, script, atom_dir, **args)

        p_ave, p_std = lammps_get_pressure(os.path.join(
            env.localroot, "results", "%s%d%s" % (config_name, i, outdir_suffix)), i)
        print("Average pressure is now", p_ave,
              "after iteration", i, "completed.")
        # if(i >= 10 and p_ave < p_std):
        #    if pressure_changed == 0:
        #        pressure = float(pressure)/3.0
        #        pressure_changed = 1
        #        print("(FabMD:) Pressure factor now set to", pressure, "after iteration", i)

        #    if abs(p_ave) - (p_std*0.5) < 0: # We have converged, let's not waste further CPU cycles!
        #        print("(FabMD:) Pressure has converged. OPTIMIZATION COMPLETE")
        #        break


@task
def full_pmf_multi(start_iter, num_iters, config_name, outdir_suffix, atom_type1, atom_type2, script="pmf.sh", atom_dir="default", **args):
    """ Do multiple PMF iterations in one command.
    Example use: fab hector full_ibi_multi:start_iter=7,num_iters=3,config_name=2peg,outdir_suffix=_hector_32,cores=32,wall_time=3:0:0 """

    if atom_dir == "default":
        atom_dir = os.path.join(env.localroot, "results",
                                "%s%d%s" % (config_name, 1, outdir_suffix))

    si = int(start_iter)
    ni = int(num_iters)

    pressure_changed = 0

    for i in xrange(si, si+ni):
        full_pmf("%s%d" % (config_name, i+1), i, "%s%d%s" % (config_name, i, outdir_suffix),
                 config_name, atom_type1, atom_type2, script, atom_dir, **args)


def lammps_get_pressure(log_dir, number):
    steps = []
    pressures = []
    LIST_IN = open(os.path.join(log_dir, "new_CG.prod%d.log" % (number)), 'r')
    for line in LIST_IN:
        NewRow = (line.strip()).split()
        if len(NewRow) > 0:
            if NewRow[0] == "Press":
                pressures.append(float(NewRow[2]))
    d1 = np.array(pressures[5:])
    print("READ: new_CG.prod%d.log" % (number))
    return np.average(d1), np.std(d1)  # average and stdev

def get_FabMD_tmp_path():
    """ Creates a directory within FabMD for file manipulation
    Once simulations are completed, its contents can be removed"""
    tmp_path = FabMD_path+"/tmp"
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    return tmp_path

@task
def easymd_example(config, **args):
    """
    Example workflow for an EasyVVUQ, FabMD LAMMPS ensemble.
    Part 1 of 2, this builds ensemble and submits the simulations

    documentation can be found in FabMD/doc/EasyVVUQ_FabMD_example.md

    config : config directory to use that contains input files
    Keyword arguments:
            cores : number of compute cores to request
            wall_time : wall-time job limit
            memory : memory per node
    """
    import easyvvuq as uq
    update_environment(args)
    with_config(config)
    config_dir = find_config_file_path(config)

    # need a tmp folder for EasyVVUQ
    tmp_path = get_FabMD_tmp_path()

    # Initialize `Campaign` object
    my_campaign = uq.Campaign(name="lammps_example", work_dir=tmp_path)

    params = {
        "velocity_seed"  : {
            "type": "int",
            "min": "1",
            "max": "1e6",
            "default":"1"},
        "data_file": {
            "type": "fixture",
            "options": "data_file",
            "default": "data_file"},
        "out_file": {
            "type": "str",
            "default": "out.csv"}}

    fixtures = {
        "data_file": {
            "type": "file",
            "path": config_dir + "/data.peptide",
            "common": False,
            "exists_local": True,
            "target": "", "group": ""}}

    # Input file containing information about parameters of interest
    easyvvuq_template = config_dir + "/lammps.template"
    easyvvuq_target = "in.lammps"
    encoder = uq.encoders.GenericEncoder(template_fname=easyvvuq_template,
                                         target_filename=easyvvuq_target,
                                         delimiter="@")

    decoder = uq.decoders.SimpleCSV(
            target_filename="out.csv",
            output_columns=["solvation_energy"],
            header=0)

    collater = uq.collate.AggregateSamples(average=False)
    my_campaign.set_collater(collater)

    # Add the cannonsim app
    my_campaign.add_app(name="lammps_example",
                        params=params,
                        encoder=encoder,
                        decoder=decoder,
                        fixtures=fixtures
                        )

    # Set parameters to vary: velocity seed will be a random integer
    vary = {"velocity_seed": uq.distributions.uniform_integer(1,1000000)}

    my_sampler = uq.sampling.RandomSampler(vary=vary)

    my_campaign.set_sampler(my_sampler)

    my_campaign.draw_samples(num_samples=5, replicas=1)

    # Encode all runs into a director in the tmp_path
    my_campaign.populate_runs_dir()

    # Save campaign state for later analysis step
    my_campaign.save_state(config_dir+'/save_campaign_state.json')

    # Convert campaign to FabSim ensemble for execution
    campaign2ensemble(config, campaign_dir=my_campaign.campaign_dir)

    # Execute lammps ensemble job
    lammps_ensemble(config, input_name_in_config=easyvvuq_target, **args)

@task
def easymd_example_analyse(config, output_dir, **args):
    """
    Example workflow for an EasyVVUQ, FabMD LAMMPS ensemble.
    Part 2 of 2, this collects simulation data and averages the results

    config : config directory to use that contains input files
    Keyword arguments:
    output_dir: name of results directory e.g. fabsim_easyvvuq_archer_24
    """
    import easyvvuq as uq
    update_environment(args)
    with_config(config)
    config_dir = find_config_file_path(config)
    tmp_path = get_FabMD_tmp_path()

    # Reload EasyVVUQ campaign state
    my_campaign = uq.Campaign(
        state_file=config_dir+"/save_campaign_state.json", work_dir=tmp_path)

    # Retrive results from execution machine and put them back into a campaign
    fetch_results()
    ensemble2campaign(env.local_results + "/" +
                      output_dir, my_campaign.campaign_dir)

    # Collect output and print raw data
    my_campaign.collate()
    print("data:", my_campaign.get_collation_result())

    # Create a BasicStats analysis element and apply it to the campaign
    stats = uq.analysis.BasicStats(qoi_cols=["solvation_energy"])
    my_campaign.apply_analysis(stats)
    print("stats:", my_campaign.get_last_analysis())


from plugins.FabFlee.gromacs_ensembles import *
