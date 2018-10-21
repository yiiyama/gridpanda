from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('config', default = '', mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.string, info = 'Single-switch config. Values: 03Feb2017, 23Sep2016, Spring16, Summer16')
options.register('globaltag', default = '', mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.string, info = 'Global tag')
options.register('connect', default = '', mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.string, info = 'Globaltag connect')
options.register('lumilist', default = '', mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.string, info = 'Good lumi list JSON')
options.register('isData', default = False, mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.bool, info = 'True if running on Data, False if running on MC')
options.register('useTrigger', default = True, mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.bool, info = 'Fill trigger information')
options.register('printLevel', default = 0, mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.int, info = 'Debug level of the ntuplizer')
options.register('skipEvents', default = 0, mult = VarParsing.multiplicity.singleton, mytype = VarParsing.varType.int, info = 'Skip first events')
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')

options.parseArguments()

options.config = 'Summer16'

jetRecorrection = False
muFix = False
egmSmearingType = 'Moriond2017_JEC'

# Global tags
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_2017_data_taking
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_PdmVMCcampaignPh

if options.config == '18Apr2017':
    options.isData = True
    options.globaltag = '80X_dataRun2_2016SeptRepro_v7'
elif options.config == 'Summer16':
    jetRecorrection = True
    muFix = True
    options.isData = False
    options.globaltag = '80X_mcRun2_asymptotic_2016_TrancheIV_v8'
elif options.config:
    raise RuntimeError('Unknown config ' + options.config)

import FWCore.ParameterSet.Config as cms

process = cms.Process('NTUPLES')

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100
for cat in ['PandaProducer', 'JetPtMismatchAtLowPt', 'JetPtMismatch', 'NullTransverseMomentum', 'MissingJetConstituent']:
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

### LUMI MASK
if options.lumilist != '':
    import FWCore.PythonUtilities.LumiList as LumiList
    process.source.lumisToProcess = LumiList.LumiList(filename = options.lumilist).getVLuminosityBlockRange()

##############
## SERVICES ##
##############

process.load('Configuration.Geometry.GeometryIdeal_cff') 
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag = options.globaltag

process.RandomNumberGeneratorService.panda = cms.PSet(
    initialSeed = cms.untracked.uint32(1234567),
    engineName = cms.untracked.string('TRandom3')
)
process.RandomNumberGeneratorService.smearedElectrons = cms.PSet(
    initialSeed = cms.untracked.uint32(89101112),
    engineName = cms.untracked.string('TRandom3')
)
process.RandomNumberGeneratorService.smearedPhotons = cms.PSet(
    initialSeed = cms.untracked.uint32(13141516),
    engineName = cms.untracked.string('TRandom3')
)

#############################
## RECO SEQUENCE AND SKIMS ##
#############################


egmCorrectionSequence = cms.Sequence()

### EGAMMA CORRECTIONS
# https://twiki.cern.ch/twiki/bin/view/CMS/EGMRegression
# https://twiki.cern.ch/twiki/bin/view/CMS/EGMSmearer

from EgammaAnalysis.ElectronTools.regressionApplication_cff import slimmedElectrons as regressionElectrons
from EgammaAnalysis.ElectronTools.regressionApplication_cff import slimmedPhotons as regressionPhotons
from EgammaAnalysis.ElectronTools.regressionWeights_cfi import regressionWeights
regressionWeights(process)
process.regressionElectrons = regressionElectrons
process.regressionPhotons = regressionPhotons

process.selectedElectrons = cms.EDFilter('PATElectronSelector',
    src = cms.InputTag('regressionElectrons'),
    cut = cms.string('pt > 5 && abs(eta) < 2.5')
)

import PandaProd.Producer.utils.egmidconf as egmidconf

from PandaProd.Producer.utils.calibratedEgamma_cfi import calibratedPatElectrons, calibratedPatPhotons
process.smearedElectrons = calibratedPatElectrons.clone(
    electrons = 'selectedElectrons',
    isMC = (not options.isData),
    correctionFile = egmidconf.electronSmearingData[egmSmearingType]
)
process.smearedPhotons = calibratedPatPhotons.clone(
    photons = 'regressionPhotons',
    isMC = (not options.isData),
    correctionFile = egmidconf.photonSmearingData[egmSmearingType]
)   

egmCorrectionSequence = cms.Sequence(
    process.regressionElectrons +
    process.regressionPhotons +
    process.selectedElectrons +
    process.smearedElectrons +
    process.smearedPhotons
)

### Vanilla MET
# this is the most basic MET one can find
# even if we override with various types of MET later on, create this so we have a consistent calo MET
# https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription

from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

runMetCorAndUncFromMiniAOD(
    process,
    isData = options.isData,
) 
metSequence = cms.Sequence(
    process.fullPatMetSequence
)

### PUPPI
# TODO find PUPPI recipes, the following doesn't look right:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/PUPPI
# From PUPPI MET recipe in
# https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription

# 80X does not contain the latest & greatest PuppiPhoton; need to rerun for all config
from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
# Creates process.puppiMETSequence which includes 'puppi' and 'puppiForMET' (= EDProducer('PuppiPhoton'))
# *UGLY* also runs switchOnVIDPhotonIdProducer and sets up photon id Spring16_V2p2 internally
# which loads photonIDValueMapProducer and egmPhotonIDs
makePuppiesFromMiniAOD(process, createScheduledSequence = True)

# Just renaming
puppiSequence = process.puppiMETSequence

# override photon ID to be consistent
process.puppiPhoton.photonId = 'egmPhotonIDs:cutBasedPhotonID-Spring16-V2p2-loose' 
process.puppiForMET.photonId = 'egmPhotonIDs:cutBasedPhotonID-Spring16-V2p2-loose' 

### PUPPI JET

from PandaProd.Producer.utils.makeJets_cff import makeJets

puppiJetSequence = makeJets(process, options.isData, 'AK4PFPuppi', 'puppi', 'Puppi')

### PUPPI MET

# Creates process.fullPatMetSequencePuppi
# With metType = 'Puppi', slimmedJetsPuppi is automatically selected as the jet source for type 1
runMetCorAndUncFromMiniAOD(
    process,
    isData = options.isData,
    metType = 'Puppi',
    pfCandColl = 'puppiForMET',
    recoMetFromPFCs = True,
    jetFlavor = 'AK4PFPuppi',
    postfix = 'Puppi'
)
# There is a bug in a function used by runMetCorAndUncFromMiniAOD (PhysicsTools.PatAlgos.tools.removeIfInSequence)
# The following module is supposed to be removed from the sequence but is not
# The bug appears when we don't call the no-postfix version of runMetCor.. first
process.fullPatMetSequencePuppi.remove(process.selectedPatJetsForMetT1T2CorrPuppi)

metSequence += process.fullPatMetSequencePuppi

### EGAMMA ID
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2 ???

from PhysicsTools.SelectorUtils.tools.vid_id_tools import setupAllVIDIdsInModule, setupVIDElectronSelection, setupVIDPhotonSelection, switchOnVIDElectronIdProducer, switchOnVIDPhotonIdProducer, DataFormat
# Loads egmGsfElectronIDs
switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
setupAllVIDIdsInModule(process, 'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff', setupVIDElectronSelection)
setupAllVIDIdsInModule(process, 'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronHLTPreselecition_Summer16_V1_cff', setupVIDElectronSelection)

switchOnVIDPhotonIdProducer(process, DataFormat.MiniAOD)
setupAllVIDIdsInModule(process, 'RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_Spring16_V2p2_cff', setupVIDPhotonSelection)

process.load('PandaProd.Auxiliary.WorstIsolationProducer_cfi')

egmIdSequence = cms.Sequence(
    process.photonIDValueMapProducer +
    process.egmPhotonIDs +
    process.egmGsfElectronIDs +
    process.worstIsolationProducer
)

### QG TAGGING

process.load('RecoJets.JetProducers.QGTagger_cfi')
process.QGTagger.srcJets = 'slimmedJets'

### FAT JETS

from PandaProd.Producer.utils.makeFatJets_cff import initFatJets, makeFatJets

# pfCHS set up here
fatJetInitSequence = initFatJets(process, options.isData, ['AK8', 'CA15'])

ak8CHSSequence = makeFatJets(
    process,
    isData = options.isData,
    label = 'AK8PFchs',
    candidates = 'pfCHS'
)

ak8PuppiSequence = makeFatJets(
    process,
    isData = options.isData,
    label = 'AK8PFPuppi',
    candidates = 'puppi'
)

ca15CHSSequence = makeFatJets(
    process,
    isData = options.isData,
    label = 'CA15PFchs',
    candidates = 'pfCHS'
)

ca15PuppiSequence = makeFatJets(
    process,
    isData = options.isData,
    label = 'CA15PFPuppi',
    candidates = 'puppi'
)

from PandaProd.Producer.utils.setupBTag import initBTag, setupDoubleBTag
initBTag(process, '', 'packedPFCandidates', 'offlineSlimmedPrimaryVertices')
ak8CHSDoubleBTagSequence = setupDoubleBTag(process, 'packedPatJetsAK8PFchs', 'AK8PFchs', '', 'ak8')
ak8PuppiDoubleBTagSequence = setupDoubleBTag(process, 'packedPatJetsAK8PFPuppi', 'AK8PFPuppi', '', 'ak8')
ca15CHSDoubleBTagSequence = setupDoubleBTag(process, 'packedPatJetsCA15PFchs', 'CA15PFchs', '', 'ca15')
ca15PuppiDoubleBTagSequence = setupDoubleBTag(process, 'packedPatJetsCA15PFPuppi', 'CA15PFPuppi', '', 'ca15')

fatJetSequence = cms.Sequence(
    fatJetInitSequence +
    ak8CHSSequence +
    ak8PuppiSequence +
    ca15CHSSequence +
    ca15PuppiSequence +
    ak8CHSDoubleBTagSequence +
    ak8PuppiDoubleBTagSequence +
    ca15CHSDoubleBTagSequence +
    ca15PuppiDoubleBTagSequence
)

### GEN JET FLAVORS
if not options.isData:
    process.load('PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi')
    from PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi import ak4JetFlavourInfos

    process.selectedHadronsAndPartons.particles = 'prunedGenParticles'

    process.ak4GenJetFlavourInfos = ak4JetFlavourInfos.clone(
        jets = 'slimmedGenJets'
    )
    process.ak8GenJetFlavourInfos = ak4JetFlavourInfos.clone(
        jets = 'genJetsNoNuAK8',
        rParam = 0.8
    )
    process.ca15GenJetFlavourInfos = ak4JetFlavourInfos.clone(
        jets = 'genJetsNoNuCA15',
        jetAlgorithm = 'CambridgeAachen',
        rParam = 1.5
    )

    genJetFlavorSequence = cms.Sequence(
        process.selectedHadronsAndPartons +
        process.ak4GenJetFlavourInfos +
        process.ak8GenJetFlavourInfos +
        process.ca15GenJetFlavourInfos
    )
else:
    genJetFlavorSequence = cms.Sequence()


if jetRecorrection:
    ### JET RE-CORRECTION
    # ???

    from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import updatedPatJetCorrFactors, updatedPatJets

    jecLevels= ['L1FastJet',  'L2Relative', 'L3Absolute']
    if options.isData:
        jecLevels.append('L2L3Residual')
    
    process.updatedPatJetCorrFactors = updatedPatJetCorrFactors.clone(
        src = cms.InputTag('slimmedJets', '', cms.InputTag.skipCurrentProcess()),
        levels = cms.vstring(*jecLevels),
    )

    process.slimmedJets = updatedPatJets.clone(
        jetSource = cms.InputTag('slimmedJets', '', cms.InputTag.skipCurrentProcess()),
        addJetCorrFactors = cms.bool(True),
        jetCorrFactorsSource = cms.VInputTag(cms.InputTag('updatedPatJetCorrFactors')),
        addBTagInfo = cms.bool(False),
        addDiscriminators = cms.bool(False)
    )

    jetRecorrectionSequence = cms.Sequence(
        process.updatedPatJetCorrFactors +
        process.slimmedJets
    )

else:
    jetRecorrectionSequence = cms.Sequence()

# runMetCorAnd.. adds a CaloMET module only once, adding the postfix
# However, repeated calls to the function overwrites the MET source of patCaloMet
process.patCaloMet.metSource = 'metrawCalo'

### MONOX FILTER

process.load('PandaProd.Filters.MonoXFilter_cfi')
process.MonoXFilter.taggingMode = True

### RECO PATH

process.reco = cms.Path(
    egmCorrectionSequence +
    egmIdSequence +
    puppiSequence +
    puppiJetSequence +
    jetRecorrectionSequence +
    metSequence +
    process.MonoXFilter +
    process.QGTagger +
    fatJetSequence +
    genJetFlavorSequence
)

#############
## NTULPES ##
#############

process.load('PandaProd.Producer.panda_cfi')
process.panda.isRealData = options.isData
process.panda.useTrigger = options.useTrigger
#process.panda.SelectEvents = ['reco'] # no skim
if options.isData:
    process.panda.fillers.partons.enabled = False
    process.panda.fillers.genParticles.enabled = False
    process.panda.fillers.ak4GenJets.enabled = False
    process.panda.fillers.ak8GenJets.enabled = False
    process.panda.fillers.ca15GenJets.enabled = False

if not options.useTrigger:
    process.panda.fillers.hlt.enabled = False

if muFix:
    process.panda.fillers.pfMet.met = 'slimmedMetsMuonFixed'

process.panda.outputFile = options.outputFile
process.panda.printLevel = options.printLevel

process.ntuples = cms.EndPath(process.panda)

##############
## SCHEDULE ##
##############

process.schedule = cms.Schedule(process.reco, process.ntuples)

############################
## REPLACE-ALL TYPE FIXES ##
############################

if muFix:
    ### PF CLEANING (BAD MUON REMOVAL)
   
    # Replace all references made so far to packedPFCandidates with cleanMuonsPFCandidates

    from PhysicsTools.PatAlgos.tools.helpers import MassSearchReplaceAnyInputTagVisitor

    replacePFCandidates = MassSearchReplaceAnyInputTagVisitor('packedPFCandidates', 'cleanMuonsPFCandidates', verbose = False)
    for everywhere in [process.producers, process.filters, process.analyzers, process.psets, process.vpsets]:
        for name, obj in everywhere.iteritems():
            replacePFCandidates.doIt(obj, name)

    process.panda.fillers.common.pfCandidates = 'cleanMuonsPFCandidates'
    process.panda.fillers.pfCandidates.puppiInput = 'cleanMuonsPFCandidates'

    from PhysicsTools.PatUtils.tools.muonRecoMitigation import muonRecoMitigation

    # Adds badGlobalMuonTaggerMAOD, cloneGlobalMuonTaggerMAOD, badMuons, and cleanMuonsPFCandidates
    muonRecoMitigation(
        process,
        pfCandCollection = 'packedPFCandidates',
        runOnMiniAOD = True
    )

    pfCleaningSequence = cms.Sequence(
        process.badMuons +
        process.cleanMuonsPFCandidates
    )

    process.reco.insert(0, pfCleaningSequence)

    ### MET
    # Recompute MET from muon-fixed PF candidates

    runMetCorAndUncFromMiniAOD(
        process,
        isData = options.isData,
        pfCandColl = 'cleanMuonsPFCandidates',
        recoMetFromPFCs = True,
        postfix = 'MuonFixed'
    )

    # see above
    process.patCaloMet.metSource = 'metrawCalo'

    process.fullPatMetSequenceMuonFixed.remove(process.selectedPatJetsForMetT1T2CorrMuonFixed)

    process.reco += process.fullPatMetSequenceMuonFixed

    process.panda.fillers.pfMet.met = 'slimmedMETsMuonFixed'

    # And of course this is against the convention (MET filters are true if event is *good*) but that's what the REMINIAOD developers chose.
    process.Flag_badMuons = cms.Path(process.badGlobalMuonTaggerMAOD)
    process.Flag_duplicateMuons = cms.Path(process.cloneGlobalMuonTaggerMAOD)
    process.schedule.insert(0, process.Flag_badMuons)
    process.schedule.insert(0, process.Flag_duplicateMuons)

if options.connect:
    if options.connect == 'mit':
        options.connect = 'frontier://(proxyurl=http://squid.cmsaf.mit.edu:3128)(proxyurl=http://squid1.cmsaf.mit.edu:3128)(proxyurl=http://squid2.cmsaf.mit.edu:3128)(serverurl=http://cmsfrontier.cern.ch:8000/FrontierProd)/CMS_CONDITIONS'

    process.GlobalTag.connect = options.connect
    for toGet in process.GlobalTag.toGet:
        toGet.connect = options.connect
