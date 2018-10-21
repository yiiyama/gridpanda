# Setup

1. Check the package out to a directory under /work on subMIT and edit the first few lines of the `submit.sh` script.
1. Create a tarball of your panda installation:
   1. Go into the panda CMSSW area and execute `cmsenv`
   1. Execute the commands in `SETUP`. A tarball named `panda_${CMSSW_RELEASE}.tar.gz` will be created in the current directory.
   1. Copy the tarball into the `cmssw` directory of the package.
1. Copy the panda processing cfg python into `pycfg` with name `(gen)panda_${CMSSW_RELEASE}.py`. 
1. If running a fullsim or fullsimmini workflow, make sure the file list for the premix library is in the `mixdata` directory.
   * If it is not, use `dasgoclient --query 'file dataset=/your/premix/library' --limit 0 | sed 's|/store|root://cmsxrootd.fnal.gov//store|' > mixdata/mixdata_LIBRARY_NAME.list; gzip mixdata/mixdata_LIBRARY_NAME.list`

# Task configuration

Each MC generation task is configured by a subdirectory of the `confs` directory. The subdirectory name corresponds to the task name and is used as the names of the log and output directories. Each subdirectory should contain two files:

1. `gen.py`: This is the CMSSW configuration for the `gen` step. Start from a typical LHE->GEN configuration for the desired campaign obtained from McM and edit the parameters for e.g. `process.externalLHEProducer` and `process.generator`. The configuration must also accept several commandline arguments (see the existing gen.py files in the repository for examples):
   * maxEvents: Number of events to generate. This parameter is defined by default when instantiating a `VarParsing` object.
   * outputFile: Name of the output file. This parameter is defined by default when instantiating a `VarParsing` object.
   * randomizeSeeds: boolean. There needs to be a block in the configuration where the seed is randomized when this is true.
   * firstLumi: uint32. Passed to `process.source`. Used to prevent event id clashes.
2. `conf.sh`: Sets the parameters for the task (r=required for all confs, f=required if TASKTYPE is fullsim or fullsimmini, d=depends on the conf, o=optional):
   * (r) GEN_ARCH: scram arch for the gen step
   * (r) GEN_RELEASE: CMSSW release (full name) for the gen step
   * (f) RECO_ARCH: scram arch for the rawsim, recosim, and miniaodsim steps
   * (f) RECO_RELEASE: CMSSW release (full name) for the rawsim, recosim, and miniaodsim steps
   * (r) PANDA_ARCH: scram arch for the panda step
   * (r) PANDA_RELEASE: CMSSW release (full name) for the panda step
   * (f) MIXDATA: Name of the mixdata list file (minus .list.gz) when 
   * (d) GEN_CMSSW: CMSSW tarball name (minus .tar.gz) for the gen step, tarball found in the cmssw/ directory
   * (d) GRIDPACKS: Space-separated list of gridpack URLs
   * (o) MAXWALLTIME: Estimated maximum wall-clock time (in minutes) of the job. Setting a good value increases the chance of getting a slot.

# Submitting jobs

```./submit.sh [-i|-t] (gen|fullsim|fullsimmini) TASKNAME [NEVENTS] [NJOBS]```

Options
`-i`: Set up an interactive execution environment in the log directory for debugging.
`-t`: Submits a single test job that runs on the subMIT execution slot.

Note: `NJOBS` cannot exceed 1000 for a technical reason (process id used for the firstLumi parameter).
