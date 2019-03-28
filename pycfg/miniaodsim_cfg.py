import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('randomizeSeeds', default = False, mytype = VarParsing.varType.bool)
options.register('ncpu', mytype = VarParsing.varType.int, default = 1)
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')
options.parseArguments()

from _miniaodsim import process

process.maxEvents.input = cms.untracked.int32(options.maxEvents)
process.source.fileNames = cms.untracked.vstring(options.inputFiles)
process.MINIAODSIMoutput.fileName = cms.untracked.string(options.outputFile)

process.options.numberOfThreads=cms.untracked.uint32(options.ncpu)

if options.randomizeSeeds:
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randSvc.populate()
