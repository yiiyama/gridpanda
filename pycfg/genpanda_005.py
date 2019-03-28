from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('globaltag', default = '', mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.string, info = 'Global tag')
options.register('connect', default = '', mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.string, info = 'Globaltag connect')
options.register('printLevel', default = 0, mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.int, info = 'Debug level of the ntuplizer')
options.register('skipEvents', default = 0, mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.int, info = 'Skip first events')
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')

options.parseArguments()

# Global tags
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_2017_data_taking
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_PdmVMCcampaignPh

options.globaltag = '80X_mcRun2_asymptotic_2016_TrancheIV_v8'

import FWCore.ParameterSet.Config as cms

process = cms.Process('NTUPLES')

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100
for cat in ['PandaProducer']:
    process.MessageLogger.categories.append(cat)
    setattr(process.MessageLogger.cerr, cat, cms.untracked.PSet(limit = cms.untracked.int32(10)))

############
## SOURCE ##
############

### INPUT FILES
process.source = cms.Source('PoolSource',
    skipEvents = cms.untracked.uint32(options.skipEvents),
    fileNames = cms.untracked.vstring(options.inputFiles)
)

### NUMBER OF EVENTS
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

##############
## SERVICES ##
##############

#process.load('Configuration.Geometry.GeometryIdeal_cff') 
#process.load('Configuration.StandardSequences.Services_cff')
#process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag = options.globaltag

##########################
## REPACK GEN PARTICLES ##
##########################

process.generatorSmeared = cms.EDProducer("GeneratorSmearedProducer",
    currentTag = cms.untracked.InputTag("VtxSmeared"),
    previousTag = cms.untracked.InputTag("generator")
)

process.genParticles = cms.EDProducer("GenParticleProducer",
    abortOnUnknownPDGCode = cms.untracked.bool(False),
    saveBarCodes = cms.untracked.bool(True),
    src = cms.InputTag("generatorSmeared")
)

from PhysicsTools.PatAlgos.slimming.genParticles_cff import prunedGenParticlesWithStatusOne
process.prunedGenParticles = prunedGenParticlesWithStatusOne.clone()

genParticleSequence = cms.Sequence(
    process.generatorSmeared +
    process.genParticles +
    process.prunedGenParticles
)

#################
## JET FLAVORS ##
#################

process.load('PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi')
from PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi import ak4JetFlavourInfos

process.selectedHadronsAndPartons.particles = 'prunedGenParticles'

process.ak4GenJetFlavourInfos = ak4JetFlavourInfos.clone(
    jets = 'ak4GenJets'
)
process.ak8GenJetFlavourInfos = ak4JetFlavourInfos.clone(
    jets = 'ak8GenJets',
    rParam = 0.8
)

genJetFlavorSequence = cms.Sequence(
    process.selectedHadronsAndPartons +
    process.ak4GenJetFlavourInfos +
    process.ak8GenJetFlavourInfos
)

### RECO PATH

process.reco = cms.Path(genParticleSequence + genJetFlavorSequence)

#############
## NTUPLES ##
#############

process.load('PandaProd.Producer.panda_cfi')
process.panda.isRealData = False
process.panda.useTrigger = False

for fname, conf in process.panda.fillers.parameters_().items():
    if fname not in ['common', 'weights', 'partons', 'genParticles', 'ak4GenJets', 'ak8GenJets']:
        getattr(process.panda.fillers, fname).enabled = False

process.panda.fillers.common.genParticles = 'prunedGenParticles'
del process.panda.fillers.common.finalStateParticles
process.panda.fillers.genParticles.outputMode = 1
process.panda.fillers.ak4GenJets.genJets = 'ak4GenJets'
process.panda.fillers.ak8GenJets.genJets = 'ak8GenJets'

process.panda.outputFile = options.outputFile
process.panda.printLevel = options.printLevel

process.ntuples = cms.EndPath(process.panda)

##############
## SCHEDULE ##
##############

process.schedule = cms.Schedule(process.reco, process.ntuples)

if options.connect:
    if options.connect == 'mit':
        options.connect = 'frontier://(proxyurl=http://squid.cmsaf.mit.edu:3128)(proxyurl=http://squid1.cmsaf.mit.edu:3128)(proxyurl=http://squid2.cmsaf.mit.edu:3128)(serverurl=http://cmsfrontier.cern.ch:8000/FrontierProd)/CMS_CONDITIONS'

    process.GlobalTag.connect = options.connect
    for toGet in process.GlobalTag.toGet:
        toGet.connect = options.connect
