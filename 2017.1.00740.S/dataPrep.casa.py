es = aU.stuffForScienceDataReduction()


###########################################################
# main program

asdm = 'uid___A002_Xd80784_X26be'
asdm = 'uid___A002_Xd80784_X2dcf'

# run in the terminal
asdmExport uid://A002/Xd80784/X2dcf

importasdm(asdm, asis='*')
vis = asdm + '.ms'
es.generateReducScript(vis)

execfile(vis+'.scriptForCalibration.py')
