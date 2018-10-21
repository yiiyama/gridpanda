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
# with command line options: Configuration/GenProduction/python/EXO-RunIISummer15wmLHEGS-02328-fragment.py --fileout file:EXO-RunIISummer15wmLHEGS-02328.root --mc --eventcontent RAWSIM,LHE --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --conditions MCRUN2_71_V1::All --beamspot Realistic50ns13TeVCollision --step LHE,GEN,SIM --magField 38T_PostLS1 --python_filename EXO-RunIISummer15wmLHEGS-02328_1_cfg.py --no_exec -n 48
import FWCore.ParameterSet.Config as cms

process = cms.Process('SIM')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.Geometry.GeometrySimDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_PostLS1_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic50ns13TeVCollision_cfi')
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
    version = cms.untracked.string('$Revision: 1.19 $'),
    annotation = cms.untracked.string('Configuration/GenProduction/python/EXO-RunIISummer15wmLHEGS-02328-fragment.py nevts:48'),
    name = cms.untracked.string('Applications')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    fileName = cms.untracked.string(options.outputFile),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('GEN-SIM')
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    )
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'MCRUN2_71_V1::All', '')

process.generator = cms.EDFilter("Pythia8HadronizerFilter",
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.0),
    maxEventsToPrint = cms.untracked.int32(1),
    PythiaParameters = cms.PSet(
        pythia8CommonSettings = cms.vstring('Tune:preferLHAPDF = 2', 
            'Main:timesAllowErrors = 10000', 
            'Check:epTolErr = 0.01', 
            'Beams:setProductionScalesFromLHEF = off', 
            'SLHA:keepSM = on', 
            'SLHA:minMassSM = 1000.', 
            'ParticleDecays:limitTau0 = on', 
            'ParticleDecays:tau0Max = 10', 
            'ParticleDecays:allowPhotonRadiation = on'),
        pythia8CUEP8M1Settings = cms.vstring('Tune:pp 14', 
            'Tune:ee 7', 
            'MultipartonInteractions:pT0Ref=2.4024', 
            'MultipartonInteractions:ecmPow=0.25208', 
            'MultipartonInteractions:expPow=1.6'),
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
            'TimeShower:weightGluonToQuark = 1'),
        processParameters = cms.vstring(
            '3000022:all = DarkPhoton void 3 0 0 0. 0. 0. 0. 0.',
            '3000022:isVisible = 0',
            '25:oneChannel = 1 1 100 22 3000022',
            'JetMatching:setMad = off', 
            'JetMatching:scheme = 1', 
            'JetMatching:merge = on', 
            'JetMatching:jetAlgorithm = 2', 
            'JetMatching:etaJetMax = 999.', 
            'JetMatching:coneRadius = 1.', 
            'JetMatching:slowJetPower = 1', 
            'JetMatching:qCut = 20.', 
            'JetMatching:doFxFx = on', 
            'JetMatching:qCutME = 10.', 
            'JetMatching:nQmatch = 5', 
            'JetMatching:nPartonsNow = 1', 
            'TimeShower:nPartonsInBorn = 1', 
            'JetMatching:nJetMax = 1'),
        parameterSets = cms.vstring('pythia8CommonSettings', 
            'pythia8CUEP8M1Settings', 
            'pythia8aMCatNLOSettings', 
            'processParameters')
    )
)


process.externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    nEvents = cms.untracked.uint32(options.maxEvents),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh'),
    numberOfParameters = cms.uint32(1),
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/slc6_amd64_gcc481/13TeV/madgraph/V5_2.2.2/zh012j_5f_NLO_FXFX_M125_ZToLL/v1/zh012j_5f_NLO_FXFX_M125_ZToLL_tarball.tar.xz')
)


# Path and EndPath definitions
process.lhe_step = cms.Path(process.externalLHEProducer)
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
if options.simStep:
    process.schedule = cms.Schedule(process.lhe_step,process.generation_step,process.genfiltersummary_step,process.simulation_step,process.endjob_step,process.RAWSIMoutput_step)
else:
    process.schedule = cms.Schedule(process.lhe_step,process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RAWSIMoutput_step)

# filter all path with the production filter sequence

for path in process.paths:
    if path in ['lhe_step']:
        continue

    getattr(process,path)._seq = process.generator * getattr(process,path)._seq 

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# Automatic addition of the customisation function from SLHCUpgradeSimulations.Configuration.postLS1Customs
from SLHCUpgradeSimulations.Configuration.postLS1Customs import customisePostLS1 

#call to customisation function customisePostLS1 imported from SLHCUpgradeSimulations.Configuration.postLS1Customs
process = customisePostLS1(process)

# End of customisation functions
if options.randomizeSeeds:
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randSvc.populate()
