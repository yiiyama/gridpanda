import os
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('firstLumi', default = 1, mytype = VarParsing.varType.int)
options.register('randomizeSeeds', default = False, mytype = VarParsing.varType.bool)
options.register('simStep', mytype = VarParsing.varType.bool, default = False)
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')
options.parseArguments()

# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: Configuration/GenProduction/python/fragment.py --fileout out.root --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE,GEN,SIM --nThreads 8 --geometry DB:Extended --era Run2_2017 --python_filename unlops_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('SIM',eras.Run2_2017)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.GeometrySimDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13TeVEarly2017Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Input source
process.source = cms.Source("EmptySource",
    firstLuminosityBlock = cms.untracked.uint32(options.firstLumi)
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('Configuration/GenProduction/python/fragment.py nevts:1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(20971520),
    fileName = cms.untracked.string(options.outputFile),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

process.LHEoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('LHE'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('out_inLHE.root'),
    outputCommands = process.LHEEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.XMLFromDBSource.label = cms.string("Extended")
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '93X_mc2017_realistic_v3', '')

process.generator = cms.EDFilter("Pythia8HadronizerFilter",
    PythiaParameters = cms.PSet(
        parameterSets = cms.vstring('pythia8CommonSettings', 
            'pythia8CP5Settings', 
            'pythia8aMCatNLOSettings', 
            'processParameters'),
        processParameters = cms.vstring('Merging:Process           = pp>mu+mu-', 
            'Merging:nJetMax           = 3', 
            'Merging:nJetMaxNLO        = 2', 
            'Merging:TMS               = 30', 
            'Merging:muFacInME         = 91.188', 
            'Merging:muRenInME         = 91.188', 
            'Merging:muFac             = 91.188', 
            'Merging:muRen             = 91.188', 
            'Merging:includeRedundant  = on', 
            'Merging:doUNLOPSTree = on',
            'SpaceShower:rapidityOrder = off'),
        pythia8CP5Settings = cms.vstring('Tune:pp 14', 
            'Tune:ee 7', 
            'MultipartonInteractions:ecmPow=0.03344', 
            'PDF:pSet=20', 
            'MultipartonInteractions:bProfile=2', 
            'MultipartonInteractions:pT0Ref=1.41', 
            'MultipartonInteractions:coreRadius=0.7634', 
            'MultipartonInteractions:coreFraction=0.63', 
            'ColourReconnection:range=5.176', 
            'SigmaTotal:zeroAXB=off', 
            'SpaceShower:alphaSorder=2', 
            'SpaceShower:alphaSvalue=0.118', 
            'SigmaProcess:alphaSvalue=0.118', 
            'SigmaProcess:alphaSorder=2', 
            'MultipartonInteractions:alphaSvalue=0.118', 
            'MultipartonInteractions:alphaSorder=2', 
            'TimeShower:alphaSorder=2', 
            'TimeShower:alphaSvalue=0.118'),
        pythia8CommonSettings = cms.vstring('Tune:preferLHAPDF = 2', 
            'Main:timesAllowErrors = 10000', 
            'Check:epTolErr = 0.01', 
            'Beams:setProductionScalesFromLHEF = off', 
            'SLHA:keepSM = on', 
            'SLHA:minMassSM = 1000.', 
            'ParticleDecays:limitTau0 = on', 
            'ParticleDecays:tau0Max = 10', 
            'ParticleDecays:allowPhotonRadiation = on'),
        pythia8aMCatNLOSettings = cms.vstring('SpaceShower:pTmaxMatch = 1', 
            'SpaceShower:pTmaxFudge = 1', 
            'SpaceShower:MEcorrections = off', 
            'TimeShower:pTmaxMatch = 1', 
            'TimeShower:pTmaxFudge = 1', 
            'TimeShower:MEcorrections = off', 
            'TimeShower:globalRecoil = on', 
            'TimeShower:limitPTmaxGlobal = on', 
            'TimeShower:nMaxGlobalRecoil = 1', 
            'TimeShower:globalRecoilMode = 2', 
            'TimeShower:nMaxGlobalBranch = 1', 
            'TimeShower:weightGluonToQuark = 1')
    ),
    comEnergy = cms.double(13000.0),
    filterEfficiency = cms.untracked.double(1.0),
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(1)
)


process.externalLHEProducer = cms.EDProducer("ExternalLHEMixingProducer",
    inputs = cms.PSet(
        lo1 = cms.PSet(
            args = cms.vstring(os.getcwd() + '/Z_LO_Inclusive_1j_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
            nPartons = cms.uint32(1),
            order = cms.string('LO')
        ),
        lo2 = cms.PSet(
            args = cms.vstring(os.getcwd() + '/Z_LO_Inclusive_2j_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
            nPartons = cms.uint32(2),
            order = cms.string('LO')
        ),
        lo3 = cms.PSet(
            args = cms.vstring(os.getcwd() + '/Z_LO_Inclusive_3j_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
            nPartons = cms.uint32(3),
            order = cms.string('LO')
        ),
        nlo0 = cms.PSet(
            args = cms.vstring(os.getcwd() + '/Z_NLO_Inclusive_0j_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
            isMain = cms.bool(True),
            nPartons = cms.uint32(0),
            order = cms.string('NLO')
        ),
        nlo1 = cms.PSet(
            args = cms.vstring(os.getcwd() + '/Z_NLO_Inclusive_1j_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
            nPartons = cms.uint32(1),
            order = cms.string('NLO')
        ),
        nlo2 = cms.PSet(
            args = cms.vstring(os.getcwd() + '/Z_NLO_Inclusive_2j_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
            nPartons = cms.uint32(2),
            order = cms.string('NLO')
        )
    ),
    nEvents = cms.untracked.uint32(int(options.maxEvents * 1.2)),
    outputFile = cms.untracked.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)


# Path and EndPath definitions
process.lhe_step = cms.Path(process.externalLHEProducer)
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)
process.LHEoutput_step = cms.EndPath(process.LHEoutput)

# Schedule definition
if options.simStep:
    process.schedule = cms.Schedule(process.lhe_step,process.generation_step,process.genfiltersummary_step,process.simulation_step,process.endjob_step,process.RAWSIMoutput_step)
else:
    process.schedule = cms.Schedule(process.lhe_step,process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RAWSIMoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads=cms.untracked.uint32(8)
process.options.numberOfStreams=cms.untracked.uint32(0)
# filter all path with the production filter sequence
for path in process.paths:
	if path in ['lhe_step']: continue
	getattr(process,path)._seq = process.generator * getattr(process,path)._seq 

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

if options.randomizeSeeds:
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randSvc.populate()
