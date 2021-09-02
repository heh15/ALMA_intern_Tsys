# ALMA Data Reduction Script

# Created using $Id: almaqa2csg.py,v 1.13 2021/02/02 22:04:56 dpetry Exp $

thesteps = []
step_title = {0: 'Import of the ASDM',
              1: 'Fix of SYSCAL table times',
              2: 'listobs',
              3: 'A priori flagging',
              4: 'Generation and time averaging of the WVR cal table',
              5: 'Generation of the Tsys cal table',
              6: 'Generation of the antenna position cal table',
              7: 'Application of the WVR, Tsys and antpos cal tables',
              8: 'Split out science SPWs and time average',
              9: 'Listobs, and save original flags',
              10: 'Initial flagging',
              11: 'Putting a model for the flux calibrator(s)',
              12: 'Save flags before bandpass cal',
              13: 'Bandpass calibration',
              14: 'Save flags before gain cal',
              15: 'Gain calibration',
              16: 'Save flags before applycal',
              17: 'Application of the bandpass and gain cal tables',
              18: 'Split out corrected column',
              19: 'Save flags after applycal'}

if 'applyonly' not in globals(): applyonly = False
try:
  print('List of steps to be executed ...'+str(mysteps))
  thesteps = mysteps
except:
  print('global variable mysteps not set.')
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print('Executing all steps: ', thesteps)

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]
# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

import re

import os

import casadef

if applyonly != True: es = aU.stuffForScienceDataReduction() 


if re.search('^5.6.1', '.'.join([str(i) for i in cu.version().tolist()[:-1]])) == None:
 sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 5.6.1')


# CALIBRATE_AMPLI: 
# CALIBRATE_ATMOSPHERE: J0914+0245,J091840.8+023047,J1058+0133
# CALIBRATE_BANDPASS: J1058+0133
# CALIBRATE_DIFFGAIN: 
# CALIBRATE_FLUX: J1058+0133
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0914+0245
# CALIBRATE_POINTING: J0914+0245,J1058+0133
# CALIBRATE_POLARIZATION: 
# OBSERVE_CHECK: J0909+0121
# OBSERVE_TARGET: J091840.8+023047

# Using reference antenna = DA45

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  if os.path.exists('uid___A002_Xd80784_X26be_v1.ms') == False:
    importasdm('uid___A002_Xd80784_X26be_v1', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=False, process_caldevice=False)
    if not os.path.exists('uid___A002_Xd80784_X26be_v1.ms.flagversions'):
      print('ERROR in importasdm. Output MS is probably not useful. Will stop here.')
      thesteps = []
  if applyonly != True: es.fixForCSV2555('uid___A002_Xd80784_X26be_v1.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xd80784_X26be_v1.ms')

print("# A priori calibration")

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.listobs')
  listobs(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    listfile = 'uid___A002_Xd80784_X26be_v1.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  flagdata(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    mode = 'manual',
    spw = '5~12,17~24',
    autocorr = True,
    flagbackup = False)
  
  flagdata(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = False)
  
  flagcmd(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xd80784_X26be_v1.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xd80784_X26be_v1.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.wvr',
    spw = [17, 19, 21, 23],
    toffset = 0,
    tie = ['J0909+0121,J0914+0245', 'J091840.8+023047,J0914+0245'],
    statsource = 'J091840.8+023047')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xd80784_X26be_v1.ms.wvr', spw='17', antenna='DA45',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xd80784_X26be_v1.ms.wvr.plots/uid___A002_Xd80784_X26be_v1.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
# mystep = 5
# if(mystep in thesteps):
#   casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
#   print('\nStep '+str(mystep)+' '+step_title[mystep])
# 
#   os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.tsys') 
#   gencal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
#     caltable = 'uid___A002_Xd80784_X26be_v1.ms.tsys',
#     caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xd80784_X26be_v1.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = False)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xd80784_X26be_v1.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=True, 
    field='', figfile='uid___A002_Xd80784_X26be_v1.ms.tsys.plots.overlayTime/uid___A002_Xd80784_X26be_v1.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xd80784_X26be_v1.ms.tsys', msName='uid___A002_Xd80784_X26be_v1.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  # Position for antenna DV12 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DA48 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DA60 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DA45 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV13 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DV14 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DA43 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DV15 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DA62 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DV08 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DV09 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV11 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV10 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV20 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DA53 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DA51 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DA56 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DA55 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV06 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DV07 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DA58 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV03 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV01 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Position for antenna DV17 is derived from baseline run made on 2019-01-06 03:03:36.
  
  # Note: the correction for antenna DV21 is larger than 2mm.
  
  # Position for antenna DV21 is derived from baseline run made on 2019-01-14 03:24:08.
  
  # Position for antenna DV05 is derived from baseline run made on 2019-01-06 03:03:36.
  
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.antpos') 
  gencal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA43,DA45,DA48,DA51,DA53,DA55,DA56,DA58,DA60,DA62,DV01,DV03,DV05,DV06,DV07,DV08,DV09,DV10,DV11,DV12,DV13,DV14,DV15,DV17,DV20,DV21',
  #  parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [6.90178e-04,-9.55714e-04,-6.48817e-04,-1.54812e-04,2.27931e-04,3.17896e-04,9.77897e-04,-1.34744e-03,-8.86969e-04,4.36569e-04,-1.18094e-03,-6.34423e-04,3.92915e-04,-8.55007e-04,-5.29384e-04,5.41995e-05,-1.69494e-04,2.94162e-04,1.81711e-04,-2.64646e-04,1.38899e-04,-1.97064e-04,3.47074e-04,4.07034e-04,-2.40984e-04,9.24631e-04,2.04492e-04,9.81401e-04,-1.03379e-03,-7.20446e-04,-3.71026e-05,1.48827e-04,2.70339e-04,1.97749e-04,-7.87264e-04,-8.41968e-05,-2.08681e-04,4.01891e-04,3.79292e-04,7.62929e-04,-1.04381e-03,-4.21335e-04,-3.32081e-04,1.54165e-04,4.18351e-04,1.09963e-03,-1.16431e-03,-8.91323e-04,-2.55422e-04,2.12388e-04,1.84627e-04,6.64007e-05,-3.02689e-05,2.74981e-04,-2.28708e-04,4.05957e-04,2.90724e-04,6.15500e-04,-1.04521e-03,-4.65605e-04,4.48743e-04,-1.03901e-03,-4.05041e-04,-2.05188e-04,5.14864e-04,4.09856e-04,7.70450e-06,-6.90248e-05,1.53069e-04,-1.89877e-04,2.34417e-04,3.39070e-04,4.35812e-04,-9.57157e-04,-4.95807e-04,1.25948e-03,-1.70037e-03,-8.30029e-04])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DV21     1.25948e-03   -1.70037e-03   -8.30029e-04    2.27300e-03      2019-01-14 03:24:08
  # DA48     9.77897e-04   -1.34744e-03   -8.86969e-04    1.88642e-03      2019-01-14 03:24:08
  # DV08     1.09963e-03   -1.16431e-03   -8.91323e-04    1.83283e-03      2019-01-14 03:24:08
  # DA62     9.81401e-04   -1.03379e-03   -7.20446e-04    1.59716e-03      2019-01-14 03:24:08
  # DA51     4.36569e-04   -1.18094e-03   -6.34423e-04    1.40986e-03      2019-01-14 03:24:08
  # DV06     7.62929e-04   -1.04381e-03   -4.21335e-04    1.35982e-03      2019-01-14 03:24:08
  # DA43     6.90178e-04   -9.55714e-04   -6.48817e-04    1.34562e-03      2019-01-14 03:24:08
  # DV12     6.15500e-04   -1.04521e-03   -4.65605e-04    1.29926e-03      2019-01-14 03:24:08
  # DV13     4.48743e-04   -1.03901e-03   -4.05041e-04    1.20207e-03      2019-01-14 03:24:08
  # DV20     4.35812e-04   -9.57157e-04   -4.95807e-04    1.16271e-03      2019-01-14 03:24:08
  # DA53     3.92915e-04   -8.55007e-04   -5.29384e-04    1.07966e-03      2019-01-14 03:24:08
  # DA60    -2.40984e-04    9.24631e-04    2.04492e-04    9.77156e-04      2019-01-14 03:24:08
  # DV03     1.97749e-04   -7.87264e-04   -8.41968e-05    8.16075e-04      2019-01-06 03:03:36
  # DV14    -2.05188e-04    5.14864e-04    4.09856e-04    6.89325e-04      2019-01-06 03:03:36
  # DV05    -2.08681e-04    4.01891e-04    3.79292e-04    5.90700e-04      2019-01-06 03:03:36
  # DA58    -1.97064e-04    3.47074e-04    4.07034e-04    5.70062e-04      2019-01-06 03:03:36
  # DV07    -3.32081e-04    1.54165e-04    4.18351e-04    5.55933e-04      2019-01-06 03:03:36
  # DV11    -2.28708e-04    4.05957e-04    2.90724e-04    5.49208e-04      2019-01-06 03:03:36
  # DV17    -1.89877e-04    2.34417e-04    3.39070e-04    4.53842e-04      2019-01-06 03:03:36
  # DA45    -1.54812e-04    2.27931e-04    3.17896e-04    4.20686e-04      2019-01-06 03:03:36
  # DV09    -2.55422e-04    2.12388e-04    1.84627e-04    3.80047e-04      2019-01-06 03:03:36
  # DA56     1.81711e-04   -2.64646e-04    1.38899e-04    3.49784e-04      2019-01-06 03:03:36
  # DA55     5.41995e-05   -1.69494e-04    2.94162e-04    3.43798e-04      2019-01-06 03:03:36
  # DV01    -3.71026e-05    1.48827e-04    2.70339e-04    3.10820e-04      2019-01-06 03:03:36
  # DV10     6.64007e-05   -3.02689e-05    2.74981e-04    2.84500e-04      2019-01-06 03:03:36
  # DV15     7.70450e-06   -6.90248e-05    1.53069e-04    1.68089e-04      2019-01-06 03:03:36
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xd80784_X26be_v1.ms', tsystable = 'uid___A002_Xd80784_X26be_v1.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    field = '0',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xd80784_X26be_v1.ms.tsys', 'uid___A002_Xd80784_X26be_v1.ms.wvr', 'uid___A002_Xd80784_X26be_v1.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    field = '1',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xd80784_X26be_v1.ms.tsys', 'uid___A002_Xd80784_X26be_v1.ms.wvr', 'uid___A002_Xd80784_X26be_v1.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J0909+0121 didn't have any Tsys measurement, so I used the one made on J091840.8+023047. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    field = '2',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xd80784_X26be_v1.ms.tsys', 'uid___A002_Xd80784_X26be_v1.ms.wvr', 'uid___A002_Xd80784_X26be_v1.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    field = '3',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xd80784_X26be_v1.ms.tsys', 'uid___A002_Xd80784_X26be_v1.ms.wvr', 'uid___A002_Xd80784_X26be_v1.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xd80784_X26be_v1.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split') 
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.flagversions') 
  
  mstransform(vis = 'uid___A002_Xd80784_X26be_v1.ms',
    outputvis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    datacolumn = 'corrected',
    spw = '17,19,21,23',
    reindex = False,
    keepflags = True)
  
  

print("# Calibration")

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.listobs')
  listobs(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    listfile = 'uid___A002_Xd80784_X26be_v1.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xd80784_X26be_v1.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    mode = 'shadow',
    flagbackup = False)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    mode = 'manual',
    spw = '17:0~7;120~127,19:0~7;120~127,21:0~7;120~127,23:0~7;120~127',
    flagbackup = False)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  setjy(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    standard = 'manual',
    field = 'J1058+0133',
    usescratch = True,
    fluxdensity = [1.72234029361, 0, 0, 0],
    spix = -0.547458323059,
    reffreq = '705.5046875GHz')
  
  # fluxDensityUncertainty = 0.0764655534173
  # meanAge = -5.0
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.ap_pre_bandpass',
    field = '0', # J1058+0133
    spw = '17:0~127,19:0~127,21:0~127,23:0~127',
    scan = '3',
    solint = 'int',
    refant = 'DA45',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xd80784_X26be_v1.ms.split.ap_pre_bandpass', msName='uid___A002_Xd80784_X26be_v1.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.bandpass',
    field = '0', # J1058+0133
    scan = '3',
    solint = 'inf',
    combine = 'scan',
    refant = 'DA45',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xd80784_X26be_v1.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xd80784_X26be_v1.ms.split.bandpass', msName='uid___A002_Xd80784_X26be_v1.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.phase_int',
    field = '0~1', # J1058+0133,J0914+0245
    solint = 'int',
    refant = 'DA45',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xd80784_X26be_v1.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xd80784_X26be_v1.ms.split.phase_int', msName='uid___A002_Xd80784_X26be_v1.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.ampli_inf',
    field = '0~1', # J1058+0133,J0914+0245
    solint = 'inf',
    refant = 'DA45',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xd80784_X26be_v1.ms.split.bandpass', 'uid___A002_Xd80784_X26be_v1.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xd80784_X26be_v1.ms.split.ampli_inf', msName='uid___A002_Xd80784_X26be_v1.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xd80784_X26be_v1.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xd80784_X26be_v1.ms.split.flux_inf',
    reference = '0') # J1058+0133
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_Xd80784_X26be_v1.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    caltable = 'uid___A002_Xd80784_X26be_v1.ms.split.phase_inf',
    field = '0~1', # J1058+0133,J0914+0245
    solint = 'inf',
    refant = 'DA45',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xd80784_X26be_v1.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xd80784_X26be_v1.ms.split.phase_inf', msName='uid___A002_Xd80784_X26be_v1.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  for i in ['0']: # J1058+0133
    applycal(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xd80784_X26be_v1.ms.split.bandpass', 'uid___A002_Xd80784_X26be_v1.ms.split.phase_int', 'uid___A002_Xd80784_X26be_v1.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = True,
      flagbackup = False)
  
  applycal(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    field = '1,2~3', # J0909+0121,J091840.8+023047
    gaintable = ['uid___A002_Xd80784_X26be_v1.ms.split.bandpass', 'uid___A002_Xd80784_X26be_v1.ms.split.phase_inf', 'uid___A002_Xd80784_X26be_v1.ms.split.flux_inf'],
    gainfield = ['', '1', '1'], # J0914+0245
    interp = 'linear,linear',
    calwt = True,
    flagbackup = False)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.cal') 
  os.system('rm -rf uid___A002_Xd80784_X26be_v1.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#AMBIENT',
   'CALIBRATE_WVR#HOT',
   'CALIBRATE_WVR#OFF_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_CHECK_SOURCE#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  mstransform(vis = 'uid___A002_Xd80784_X26be_v1.ms.split',
    outputvis = 'uid___A002_Xd80784_X26be_v1.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = True)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xd80784_X26be_v1.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

