asdmExport uid://A002/Xbf792a/X14cc

import analysisUtils as aU
es = aU.stuffForScienceDataReduction()

# import asdm file
asdm = 'uid___A002_Xbf792a_X14cc'
importasdm(asdm, asis='*') 
vis = asdm+'.ms'

# generate calibration script
es.generateReducScript(vis)

