# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-00049-fragment.py --fileout file:HIG-RunIIFall17wmLHEGS-00049.root --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE,GEN,SIM --nThreads 8 --geometry DB:Extended --era Run2_2017 --python_filename HIG-RunIIFall17wmLHEGS-00049_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=int(1550157978%100) -n 697
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
    input = cms.untracked.int32(1)
)

# Input source
process.source = cms.Source("EmptySource",
    firstLuminosityBlock = cms.untracked.uint32(1)
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-00049-fragment.py nevts:697'),
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
    fileName = cms.untracked.string('out.root'),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

#process.LHEoutput = cms.OutputModule("PoolOutputModule",
#    dataset = cms.untracked.PSet(
#        dataTier = cms.untracked.string('LHE'),
#        filterName = cms.untracked.string('')
#    ),
#    fileName = cms.untracked.string('file:HIG-RunIIFall17wmLHEGS-00049_inLHE.root'),
#    outputCommands = process.LHEEventContent.outputCommands,
#    splitLevel = cms.untracked.int32(0)
#)

# Additional output definition

# Other statements
process.XMLFromDBSource.label = cms.string("Extended")
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '93X_mc2017_realistic_v3', '')

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.Pythia8aMCatNLOSettings_cfi import *
#from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

process.generator = cms.EDFilter("Pythia8HadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.0),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8aMCatNLOSettingsBlock,
        #pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
            'JetMatching:setMad = off', 
            'JetMatching:scheme = 1', 
            'JetMatching:merge = on', 
            'JetMatching:jetAlgorithm = 2', 
            'JetMatching:etaJetMax = 999.', 
            'JetMatching:coneRadius = 1.', 
            'JetMatching:slowJetPower = 1', 
            'JetMatching:qCut = 45.', 
            'JetMatching:doFxFx = on', 
            'JetMatching:qCutME = 30.', 
            'JetMatching:nQmatch = 5', 
            'JetMatching:nJetMax = 2', 
            'TimeShower:mMaxGamma = 4.0'
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings', 
            'pythia8CP5Settings', 
            'pythia8aMCatNLOSettings', 
            #'pythia8PSweightsSettings',
            'processParameters'
        )
    )
)

from RecoJets.Configuration.GenJetParticles_cff import genParticlesForJetsNoNu
from RecoJets.Configuration.RecoGenJets_cff import ak4GenJetsNoNu

# Filter out PromptFinalState photons
process.genParticlesNoGamma = cms.EDFilter('CandPtrSelector',
    src = cms.InputTag('genParticles'),
    cut = cms.string('pdgId != 22 || !isPromptFinalState')
)

process.genParticlesForJetsNoNuNoGamma = genParticlesForJetsNoNu.clone(
    src = cms.InputTag("genParticlesNoGamma")
)

process.ak4GenJetsNoNuNoGamma = ak4GenJetsNoNu.clone(
    src = cms.InputTag("genParticlesForJetsNoNuNoGamma")
)

process.vbfGenJetFilterD = cms.EDFilter("VBFGenJetFilter",
    inputTag_GenJetCollection = cms.untracked.InputTag("ak4GenJetsNoNuNoGamma"),
    maxEta = cms.untracked.double(99999.0),
    minEta = cms.untracked.double(-99999.0),
    minInvMass = cms.untracked.double(400.),
    minPt = cms.untracked.double(30.)
)

from GeneratorInterface.Core.generatorSmeared_cfi import generatorSmeared
from PhysicsTools.HepMCCandAlgos.genParticles_cfi import genParticles

process.ProductionFilterSequence = cms.Sequence(
    process.generator+
    cms.SequencePlaceholder('randomEngineStateProducer')+
    cms.SequencePlaceholder('VtxSmeared')+
    process.generatorSmeared+
    process.genParticles+
    process.genParticlesNoGamma+
    process.genParticlesForJetsNoNuNoGamma+
    process.ak4GenJetsNoNuNoGamma+
    process.vbfGenJetFilterD+
    cms.SequencePlaceholder("pgen")
)

process.SimFilterSequence = cms.Sequence(
    process.vbfGenJetFilterD+
    cms.SequencePlaceholder("psim")
)

process.externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring(),
    nEvents = cms.untracked.uint32(1),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

# Path and EndPath definitions
process.lhe_step = cms.Path(process.externalLHEProducer)
process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)
#process.LHEoutput_step = cms.EndPath(process.LHEoutput)

# Schedule definition
process.schedule = cms.Schedule(process.lhe_step,process.generation_step,process.genfiltersummary_step,process.simulation_step,process.endjob_step,process.RAWSIMoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads=cms.untracked.uint32(8)
process.options.numberOfStreams=cms.untracked.uint32(0)
# filter all path with the production filter sequence
for path in process.paths:
	if path in ['lhe_step']: continue
	getattr(process,path)._seq = process.ProductionFilterSequence * getattr(process,path)._seq 

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# End of customisation functions

# Customisation from command line

#process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=int(1550157978%100)
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
