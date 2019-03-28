import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('randomizeSeeds', default = False, mytype = VarParsing.varType.bool)
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')
options.parseArguments()

from _recosim import process

process.maxEvents.input = cms.untracked.int32(options.maxEvents)

process.source.fileNames = cms.untracked.vstring(options.inputFiles)

process.AODSIMoutput.fileName = cms.untracked.string(options.outputFile)

if options.randomizeSeeds:
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randSvc.populate()
