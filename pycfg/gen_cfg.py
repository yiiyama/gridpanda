import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('firstLumi', default = 1, mytype = VarParsing.varType.int)
options.register('randomizeSeeds', default = False, mytype = VarParsing.varType.bool)
options.register('simStep', mytype = VarParsing.varType.bool, default = False)
options.register('gridpacks', mytype = VarParsing.varType.string, mult = VarParsing.multiplicity.list)
options._tags.pop('numEvent%d')
options._tagOrder.remove('numEvent%d')
options.parseArguments()

from _gen import process

process.maxEvents.input = cms.untracked.int32(options.maxEvents)
process.source.firstLuminosityBlock = cms.untracked.uint32(options.firstLumi)
process.RAWSIMoutput.fileName = cms.untracked.string(options.outputFile)
process.externalLHEProducer.nEvents = cms.untracked.uint32(options.maxEvents)
if len(options.gridpacks):
    for gp in options.gridpacks:
        process.externalLHEProducer.args.append(gp)

if not options.simStep:
    process.schedule.remove(process.simulation_step)

if options.randomizeSeeds:
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randSvc.populate()
