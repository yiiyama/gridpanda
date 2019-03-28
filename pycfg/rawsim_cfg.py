import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('mixdata', default = 'mixdata.list', mytype = VarParsing.varType.string)
options.register('randomizeSeeds', default = False, mytype = VarParsing.varType.bool)
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')
options.parseArguments()

from _rawsim import process

process.maxEvents.input = cms.untracked.int32(options.maxEvents)
process.source.fileNames = cms.untracked.vstring(options.inputFiles)
process.PREMIXRAWoutput.fileName = cms.untracked.string(options.outputFile)

mixFiles = []
with open(options.mixdata) as src:
    for line in src:
        mixFiles.append(line.strip())

process.mixData.input.fileNames = mixFiles

if options.randomizeSeeds:
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randSvc.populate()
