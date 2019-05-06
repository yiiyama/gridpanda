from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')
options.parseArguments()

import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

process = cms.Process('NTUPLES',eras.Phase2C4_timing_layer_bar)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles)
)

process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2023D35Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.L1TrackTrigger_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
process.load('HLTrigger.Configuration.HLT_Fake2_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(options.outputFile)
)

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100

# Other statements
process.mix.digitizers = cms.PSet(process.theDigitizersValid)
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '103X_upgrade2023_realistic_v2', '')

process.kinFilter = cms.EDFilter('CandViewSelector',
    src = cms.InputTag('genParticles'),
    cut = cms.string('pt > 5 && abs(eta) > 1.45 && abs(eta) < 2.8'),
    filter = cms.bool(True)
)

process.load('L1Trigger.L1THGCal.hgcalTriggerPrimitives_cff')
process.load('L1Trigger.L1THGCalUtilities.hgcalTriggerNtuples_cff')
process.load('L1Trigger.L1THGCalUtilities.caloTruthCellsProducer_cfi')
process.hgcalTriggerPrimitives += process.caloTruthCellsProducer
process.caloTruthCellsProducer.makeCellsCollection = False
process.load('L1Trigger.L1THGCalUtilities.caloTruthCellsNtuples_cff')

for pset in list(process.hgcalTriggerNtuplizer.Ntuples):
    if pset.NtupleName in ['HGCalTriggerNtupleGenTau', 'HGCalTriggerNtupleGenJet', 'HGCalTriggerNtupleHGCDigis', 'HGCalTriggerNtupleHGCPanels', 'HGCalTriggerNtupleHGCTowers']:
        process.hgcalTriggerNtuplizer.Ntuples.remove(pset)

    elif hasattr(pset, 'Prefix') and pset.Prefix in ['tctruth', 'cl3dfulltruth', 'cl3dtruth']:
        process.hgcalTriggerNtuplizer.Ntuples.remove(pset)

    elif pset.NtupleName == 'HGCalTriggerNtupleHGCTriggerCells':
        pset.FillTruthMap = True

    elif pset.NtupleName == 'HGCalTriggerNtupleHGCMulticlusters' and not hasattr(pset, 'Prefix'):
        pset.MatchSimTrack = cms.untracked.bool(True)
        pset.SimTracks = cms.InputTag('g4SimHits')
        pset.SimVertices = cms.InputTag('g4SimHits')
        pset.SimHitsEE = cms.InputTag('g4SimHits', 'HGCHitsEE')
        pset.SimHitsHEfront = cms.InputTag('g4SimHits', 'HGCHitsHEfront')
        pset.SimHitsHEback = cms.InputTag('g4SimHits', 'HGCHitsHEback')

# first modules of digitisation_step come before kinFilter (GeneInfo = [genParticles])
process.GeneInfo += process.kinFilter

process.digitisation_step = cms.Path(process.pdigi_valid)
process.hgcl1tpg_step = cms.Path(process.kinFilter + process.hgcalTriggerPrimitives + process.hgcalTriggerNtuples)
process.L1simulation_step = cms.Path(process.kinFilter + process.SimL1Emulator)
#process.digi2raw_step = cms.Path(process.DigiToRaw)
process.endjob_step = cms.EndPath(process.endOfProcess)

process.schedule = cms.Schedule(process.digitisation_step, process.hgcl1tpg_step, process.L1simulation_step, process.endjob_step)
