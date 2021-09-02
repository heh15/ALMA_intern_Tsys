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
# CALIBRATE_ATMOSPHERE: IRAS16293_A,J1256-0547,J1626-2951
# CALIBRATE_BANDPASS: J1256-0547
# CALIBRATE_DIFFGAIN: 
# CALIBRATE_FLUX: J1256-0547
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J1626-2951
# CALIBRATE_POINTING: J1256-0547,J1626-2951
# CALIBRATE_POLARIZATION: 
# OBSERVE_CHECK: J1625-2527
# OBSERVE_TARGET: IRAS16293_A,IRAS16293_B

# Using reference antenna = DV04

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  if os.path.exists('uid___A002_Xbf792a_X14cc_v1.ms') == False:
    importasdm('uid___A002_Xbf792a_X14cc_v1', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=False, process_caldevice=False)
    if not os.path.exists('uid___A002_Xbf792a_X14cc_v1.ms.flagversions'):
      print('ERROR in importasdm. Output MS is probably not useful. Will stop here.')
      thesteps = []
  if applyonly != True: es.fixForCSV2555('uid___A002_Xbf792a_X14cc_v1.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xbf792a_X14cc_v1.ms')

print("# A priori calibration")

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.listobs')
  listobs(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    listfile = 'uid___A002_Xbf792a_X14cc_v1.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  flagdata(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    mode = 'manual',
    spw = '5~12,17~42',
    autocorr = True,
    flagbackup = False)
  
  flagdata(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = False)
  
  flagcmd(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xbf792a_X14cc_v1.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.wvrgcal') 
  
  # Warning: more than one integration time found on science data, I'm picking the lowest value. Please check this is right.
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xbf792a_X14cc_v1.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.wvr',
    spw = [23, 25, 27, 29, 31, 33, 35, 37, 39, 41],
    toffset = 0,
    tie = ['IRAS16293_A,J1626-2951', 'IRAS16293_B,J1626-2951', 'J1625-2527,J1626-2951'],
    statsource = 'IRAS16293_A')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xbf792a_X14cc_v1.ms.wvr', spw='23', antenna='DV04',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xbf792a_X14cc_v1.ms.wvr.plots/uid___A002_Xbf792a_X14cc_v1.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

#   os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.tsys') 
#   gencal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
#     caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.tsys',
#     caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = False)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xbf792a_X14cc_v1.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=True, 
    field='', figfile='uid___A002_Xbf792a_X14cc_v1.ms.tsys.plots.overlayTime/uid___A002_Xbf792a_X14cc_v1.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbf792a_X14cc_v1.ms.tsys', msName='uid___A002_Xbf792a_X14cc_v1.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  # Position for antenna DV12 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV18 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA64 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA49 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA48 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA61 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA47 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA46 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV17 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA42 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV23 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV15 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV08 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV11 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA52 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA53 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV22 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA51 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV24 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA54 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DA55 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV06 is derived from baseline run made on 2017-05-02 03:52:08.
  
  # Position for antenna DV07 is derived from baseline run made on 2017-05-02 03:52:08.
  
  # Position for antenna DV04 is derived from baseline run made on 2017-05-09 07:38:12.
  
  # Position for antenna DV05 is derived from baseline run made on 2017-05-02 03:52:08.
  
  # Position for antenna DV01 is derived from baseline run made on 2017-05-02 03:52:08.
  
  # Position for antenna DV13 is derived from baseline run made on 2017-05-09 07:38:12.
  
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.antpos') 
  gencal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA42,DA46,DA47,DA48,DA49,DA51,DA52,DA53,DA54,DA55,DA61,DA64,DV01,DV04,DV05,DV06,DV07,DV08,DV11,DV12,DV13,DV15,DV17,DV18,DV22,DV23,DV24',
  #  parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [7.38818e-06,1.65836e-04,-1.64290e-05,-2.40632e-04,5.59761e-04,3.64186e-04,-2.83890e-04,6.32737e-04,2.61087e-04,-1.71196e-04,3.13099e-04,9.55188e-05,-8.57348e-05,2.66009e-04,1.39429e-04,-7.20015e-05,1.01702e-04,1.73528e-04,-2.38004e-05,-9.04063e-05,4.64073e-05,-1.64230e-04,4.24679e-04,2.25213e-04,-2.62036e-04,2.09262e-04,-2.21408e-05,6.22673e-05,-1.90698e-04,4.20068e-05,-5.74859e-06,1.06900e-04,-1.08364e-05,-1.24527e-04,6.58780e-05,5.07608e-05,1.17555e-04,-4.98736e-04,-4.77489e-04,7.27517e-05,8.23932e-05,1.48010e-04,3.05963e-04,-6.52968e-04,-5.59197e-04,-1.30580e-05,-4.25059e-04,-1.10840e-04,1.55351e-04,-8.02435e-04,-4.64308e-04,-4.10224e-05,-3.18398e-04,-5.97346e-05,1.41046e-04,-2.57370e-04,-6.35209e-06,-6.99339e-05,2.00899e-04,1.12842e-04,-1.12550e-04,4.72357e-05,1.21333e-04,4.58971e-04,-9.74033e-04,-3.04503e-04,-1.70902e-05,2.67725e-04,-4.29372e-05,-1.76931e-04,3.57925e-04,3.19393e-04,-5.09527e-06,1.42354e-04,2.37736e-04,2.85511e-05,8.84143e-04,3.69776e-04,7.19968e-05,3.78769e-05,4.95831e-05])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DV15     4.58971e-04   -9.74033e-04   -3.04503e-04    1.11898e-03      2017-05-09 07:38:12
  # DV23     2.85511e-05    8.84143e-04    3.69776e-04    9.58779e-04      2017-05-09 07:38:12
  # DV07     1.55351e-04   -8.02435e-04   -4.64308e-04    9.40009e-04      2017-05-02 03:52:08
  # DV05     3.05963e-04   -6.52968e-04   -5.59197e-04    9.12514e-04      2017-05-02 03:52:08
  # DA47    -2.83890e-04    6.32737e-04    2.61087e-04    7.41024e-04      2017-05-09 07:38:12
  # DA46    -2.40632e-04    5.59761e-04    3.64186e-04    7.09836e-04      2017-05-09 07:38:12
  # DV01     1.17555e-04   -4.98736e-04   -4.77489e-04    7.00395e-04      2017-05-02 03:52:08
  # DV18    -1.76931e-04    3.57925e-04    3.19393e-04    5.11299e-04      2017-05-09 07:38:12
  # DA53    -1.64230e-04    4.24679e-04    2.25213e-04    5.07981e-04      2017-05-09 07:38:12
  # DV06    -1.30580e-05   -4.25059e-04   -1.10840e-04    4.39467e-04      2017-05-02 03:52:08
  # DA48    -1.71196e-04    3.13099e-04    9.55188e-05    3.69409e-04      2017-05-09 07:38:12
  # DA54    -2.62036e-04    2.09262e-04   -2.21408e-05    3.36071e-04      2017-05-09 07:38:12
  # DV08    -4.10224e-05   -3.18398e-04   -5.97346e-05    3.26540e-04      2017-05-09 07:38:12
  # DA49    -8.57348e-05    2.66009e-04    1.39429e-04    3.12333e-04      2017-05-09 07:38:12
  # DV11     1.41046e-04   -2.57370e-04   -6.35209e-06    2.93554e-04      2017-05-09 07:38:12
  # DV22    -5.09527e-06    1.42354e-04    2.37736e-04    2.77144e-04      2017-05-09 07:38:12
  # DV17    -1.70902e-05    2.67725e-04   -4.29372e-05    2.71684e-04      2017-05-09 07:38:12
  # DV12    -6.99339e-05    2.00899e-04    1.12842e-04    2.40800e-04      2017-05-09 07:38:12
  # DA51    -7.20015e-05    1.01702e-04    1.73528e-04    2.13634e-04      2017-05-09 07:38:12
  # DA55     6.22673e-05   -1.90698e-04    4.20068e-05    2.04957e-04      2017-05-09 07:38:12
  # DV04     7.27517e-05    8.23932e-05    1.48010e-04    1.84360e-04      2017-05-09 07:38:12
  # DV13    -1.12550e-04    4.72357e-05    1.21333e-04    1.72106e-04      2017-05-09 07:38:12
  # DA42     7.38818e-06    1.65836e-04   -1.64290e-05    1.66811e-04      2017-05-09 07:38:12
  # DA64    -1.24527e-04    6.58780e-05    5.07608e-05    1.49745e-04      2017-05-09 07:38:12
  # DA61    -5.74859e-06    1.06900e-04   -1.08364e-05    1.07602e-04      2017-05-09 07:38:12
  # DA52    -2.38004e-05   -9.04063e-05    4.64073e-05    1.04371e-04      2017-05-09 07:38:12
  # DV24     7.19968e-05    3.78769e-05    4.95831e-05    9.52717e-05      2017-05-09 07:38:12
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xbf792a_X14cc_v1.ms', tsystable = 'uid___A002_Xbf792a_X14cc_v1.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    field = '0',
    spw = '23,25,27,29,31,33,35,37,39,41',
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.tsys', 'uid___A002_Xbf792a_X14cc_v1.ms.wvr', 'uid___A002_Xbf792a_X14cc_v1.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    field = '1',
    spw = '23,25,27,29,31,33,35,37,39,41',
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.tsys', 'uid___A002_Xbf792a_X14cc_v1.ms.wvr', 'uid___A002_Xbf792a_X14cc_v1.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J1625-2527 didn't have any Tsys measurement, so I used the one made on IRAS16293_A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    field = '2',
    spw = '23,25,27,29,31,33,35,37,39,41',
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.tsys', 'uid___A002_Xbf792a_X14cc_v1.ms.wvr', 'uid___A002_Xbf792a_X14cc_v1.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    field = '3',
    spw = '23,25,27,29,31,33,35,37,39,41',
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.tsys', 'uid___A002_Xbf792a_X14cc_v1.ms.wvr', 'uid___A002_Xbf792a_X14cc_v1.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: IRAS16293_B didn't have any Tsys measurement, so I used the one made on IRAS16293_A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    field = '4',
    spw = '23,25,27,29,31,33,35,37,39,41',
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.tsys', 'uid___A002_Xbf792a_X14cc_v1.ms.wvr', 'uid___A002_Xbf792a_X14cc_v1.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xbf792a_X14cc_v1.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split') 
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.flagversions') 
  
  mstransform(vis = 'uid___A002_Xbf792a_X14cc_v1.ms',
    outputvis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    datacolumn = 'corrected',
    spw = '23,25,27,29,31,33,35,37,39,41',
    reindex = False,
    keepflags = True)
  
  

print("# Calibration")

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.listobs')
  listobs(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    listfile = 'uid___A002_Xbf792a_X14cc_v1.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xbf792a_X14cc_v1.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    mode = 'shadow',
    flagbackup = False)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    mode = 'manual',
    spw = '23:0~7;120~127',
    flagbackup = False)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  setjy(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    standard = 'manual',
    field = 'J1256-0547',
    usescratch = True,
    fluxdensity = [4.41658635695, 0, 0, 0],
    spix = -0.532106764439,
    reffreq = '616.019581404GHz')
  
  # fluxDensityUncertainty = 0.0805982922973
  # meanAge = 0.0
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.ap_pre_bandpass',
    field = '0', # J1256-0547
    spw = '23:0~127,25:0~479,27:0~479,29:0~959,31:0~479,33:0~959,35:0~479,37:0~479,39:0~479,41:0~959',
    scan = '3',
    solint = 'int',
    refant = 'DV04',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbf792a_X14cc_v1.ms.split.ap_pre_bandpass', msName='uid___A002_Xbf792a_X14cc_v1.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass',
    field = '0', # J1256-0547
    scan = '3',
    solint = 'inf',
    combine = 'scan',
    refant = 'DV04',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass', msName='uid___A002_Xbf792a_X14cc_v1.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.phase_int',
    field = '0~1', # J1256-0547,J1626-2951
    solint = 'int',
    refant = 'DV04',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbf792a_X14cc_v1.ms.split.phase_int', msName='uid___A002_Xbf792a_X14cc_v1.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.ampli_inf',
    field = '0~1', # J1256-0547,J1626-2951
    solint = 'inf',
    refant = 'DV04',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass', 'uid___A002_Xbf792a_X14cc_v1.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbf792a_X14cc_v1.ms.split.ampli_inf', msName='uid___A002_Xbf792a_X14cc_v1.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xbf792a_X14cc_v1.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.flux_inf',
    reference = '0') # J1256-0547
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_Xbf792a_X14cc_v1.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    caltable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.phase_inf',
    field = '0~1', # J1256-0547,J1626-2951
    solint = 'inf',
    refant = 'DV04',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbf792a_X14cc_v1.ms.split.phase_inf', msName='uid___A002_Xbf792a_X14cc_v1.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  for i in ['0']: # J1256-0547
    applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass', 'uid___A002_Xbf792a_X14cc_v1.ms.split.phase_int', 'uid___A002_Xbf792a_X14cc_v1.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = True,
      flagbackup = False)
  
  applycal(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    field = '1,2~4', # IRAS16293_A,IRAS16293_B,J1625-2527
    gaintable = ['uid___A002_Xbf792a_X14cc_v1.ms.split.bandpass', 'uid___A002_Xbf792a_X14cc_v1.ms.split.phase_inf', 'uid___A002_Xbf792a_X14cc_v1.ms.split.flux_inf'],
    gainfield = ['', '1', '1'], # J1626-2951
    interp = 'linear,linear',
    calwt = True,
    flagbackup = False)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.cal') 
  os.system('rm -rf uid___A002_Xbf792a_X14cc_v1.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#AMBIENT',
   'CALIBRATE_WVR#HOT',
   'CALIBRATE_WVR#OFF_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_CHECK_SOURCE#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  mstransform(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split',
    outputvis = 'uid___A002_Xbf792a_X14cc_v1.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = True)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('\nStep '+str(mystep)+' '+step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbf792a_X14cc_v1.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

