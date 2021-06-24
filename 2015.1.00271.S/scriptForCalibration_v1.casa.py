# ALMA Data Reduction Script
import analysisUtils as aU

def count_time(stop, start):
    '''
    Convert the time difference into human readable form. 
    '''
    dure=stop-start
    m,s=divmod(dure,60)
    h,m=divmod(m,60)
    print("%d:%02d:%02d" %(h, m, s))

    return

start = time.time()

# Calibration

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
  print('List of steps to be executed ...', mysteps)
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
# CALIBRATE_ATMOSPHERE: Arp220,J1256-0547,J1504+1029
# CALIBRATE_BANDPASS: J1256-0547
# CALIBRATE_DIFFGAIN: 
# CALIBRATE_FLUX: J1256-0547
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J1504+1029
# CALIBRATE_POINTING: J1256-0547,J1504+1029
# CALIBRATE_POLARIZATION: 
# OBSERVE_CHECK: J1516+1932
# OBSERVE_TARGET: Arp220

# Using reference antenna = DV10

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  if os.path.exists('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms') == False:
    importasdm('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=False, process_caldevice=False)
    if not os.path.exists('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.flagversions'):
      print('ERROR in importasdm. Output MS is probably not useful. Will stop here.')
      thesteps = []
  if applyonly != True: es.fixForCSV2555('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms')

print("# A priori calibration")

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.listobs')
  listobs(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    listfile = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    mode = 'manual',
    spw = '5~12,17~24',
    autocorr = True,
    flagbackup = False)
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = False)
  
  flagcmd(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr',
    spw = [17, 19, 21, 23],
    toffset = 0,
    tie = ['J1516+1932,J1504+1029', 'Arp220,J1504+1029'],
    statsource = 'Arp220')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr', spw='17', antenna='DV10',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr.plots/uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

#   os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys') 
#   gencal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
#     caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys',
#     caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = False)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=True, 
    field='', figfile='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys.plots.overlayTime/uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  # Warning: no baseline run found for following antenna(s): ['DA41', 'DA55'].
  
  # Position for antenna DV18 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA65 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA64 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA63 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA48 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA61 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA60 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV11 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: the correction for antenna DA44 is larger than 2mm.
  
  # Position for antenna DA44 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA47 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA46 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV14 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA43 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV23 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV25 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA49 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA62 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV08 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV09 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV19 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV22 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV04 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA53 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA50 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DA51 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA56 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA57 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA54 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV06 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA58 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DA59 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV03 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV01 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV17 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV16 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV13 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV05 is derived from baseline run made on 2017-03-27 08:15:07.
  
  # Position for antenna DV24 is derived from baseline run made on 2017-03-27 08:15:07.
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.antpos') 
  gencal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA43,DA44,DA46,DA47,DA48,DA49,DA50,DA51,DA53,DA54,DA56,DA57,DA58,DA59,DA60,DA61,DA62,DA63,DA64,DA65,DV01,DV03,DV04,DV05,DV06,DV08,DV09,DV11,DV13,DV14,DV16,DV17,DV18,DV19,DV22,DV23,DV24,DV25',
  #  parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [-5.19599e-04,1.34785e-03,8.00997e-04,-5.00629e-04,2.00061e-03,8.16823e-04,1.69917e-06,1.51697e-04,3.40466e-05,1.32879e-04,7.39910e-05,-8.67609e-05,-1.60115e-05,1.26317e-04,-1.10347e-05,9.56579e-06,9.01965e-05,2.93782e-05,-3.02855e-04,1.75168e-04,9.51592e-05,-8.68686e-05,2.74559e-04,1.28286e-04,1.50203e-05,1.00634e-04,4.99528e-05,-2.77324e-04,6.08710e-04,1.58042e-04,-1.73599e-04,3.84565e-04,4.88581e-05,-1.77989e-04,2.39685e-04,1.63373e-04,-1.15305e-04,2.22557e-04,8.81217e-06,-1.97908e-04,3.54432e-04,7.13694e-05,-8.52593e-05,3.40767e-04,6.17569e-05,2.98899e-05,4.41484e-04,2.02515e-04,3.89847e-05,1.97892e-04,1.24916e-05,-7.55373e-05,9.48693e-05,1.22445e-05,-1.27210e-04,3.08263e-04,1.74125e-05,-1.08856e-04,3.37461e-04,6.24439e-05,-1.33054e-04,-7.52535e-06,-1.82488e-04,1.39480e-04,-1.38293e-04,-1.87401e-05,9.37773e-05,6.92129e-05,-3.67884e-05,-5.63888e-05,-7.58469e-06,-3.86476e-05,7.51251e-06,7.38157e-05,8.89474e-05,3.63952e-05,-1.39949e-04,-6.12251e-05,-7.09007e-05,-3.66932e-05,2.81944e-05,-7.10332e-05,-3.94258e-04,-3.22901e-04,8.23829e-05,9.97679e-05,2.66202e-04,-6.47395e-05,6.25374e-05,-1.05502e-04,2.33115e-05,1.64894e-04,2.70651e-05,4.78101e-05,-5.94730e-06,7.90432e-05,6.82778e-05,-5.17441e-07,8.54919e-05,9.35282e-05,1.49068e-04,-7.06687e-05,-2.14049e-04,-1.07558e-05,-1.58949e-04,-7.98581e-05,5.53597e-05,1.16870e-04,7.18268e-05,2.77864e-05,-7.87771e-05,-4.01706e-04,1.10556e-03,1.50060e-04])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DA44    -5.00629e-04    2.00061e-03    8.16823e-04    2.21817e-03      2017-03-27 08:15:07
  # DA43    -5.19599e-04    1.34785e-03    8.00997e-04    1.65175e-03      2017-03-27 08:15:07
  # DV25    -4.01706e-04    1.10556e-03    1.50060e-04    1.18581e-03      2017-03-27 08:15:07
  # DA54    -2.77324e-04    6.08710e-04    1.58042e-04    6.87323e-04      2017-03-27 08:15:07
  # DV11    -7.10332e-05   -3.94258e-04   -3.22901e-04    5.14539e-04      2017-03-19 07:39:48
  # DA61     2.98899e-05    4.41484e-04    2.02515e-04    4.86635e-04      2017-03-27 08:15:07
  # DA56    -1.73599e-04    3.84565e-04    4.88581e-05    4.24751e-04      2017-03-27 08:15:07
  # DA59    -1.97908e-04    3.54432e-04    7.13694e-05    4.12169e-04      2017-03-27 08:15:07
  # DA50    -3.02855e-04    1.75168e-04    9.51592e-05    3.62574e-04      2017-03-19 07:39:48
  # DA65    -1.08856e-04    3.37461e-04    6.24439e-05    3.60040e-04      2017-03-27 08:15:07
  # DA60    -8.52593e-05    3.40767e-04    6.17569e-05    3.56659e-04      2017-03-27 08:15:07
  # DA57    -1.77989e-04    2.39685e-04    1.63373e-04    3.40323e-04      2017-03-27 08:15:07
  # DA64    -1.27210e-04    3.08263e-04    1.74125e-05    3.33934e-04      2017-03-27 08:15:07
  # DA51    -8.68686e-05    2.74559e-04    1.28286e-04    3.15256e-04      2017-03-27 08:15:07
  # DV13     8.23829e-05    9.97679e-05    2.66202e-04    2.95980e-04      2017-03-27 08:15:07
  # DV22    -2.14049e-04   -1.07558e-05   -1.58949e-04    2.66828e-04      2017-03-27 08:15:07
  # DA58    -1.15305e-04    2.22557e-04    8.81217e-06    2.50808e-04      2017-03-27 08:15:07
  # DV01    -1.33054e-04   -7.52535e-06   -1.82488e-04    2.25969e-04      2017-03-27 08:15:07
  # DA62     3.89847e-05    1.97892e-04    1.24916e-05    2.02082e-04      2017-03-27 08:15:07
  # DV03     1.39480e-04   -1.38293e-04   -1.87401e-05    1.97309e-04      2017-03-27 08:15:07
  # DV19     9.35282e-05    1.49068e-04   -7.06687e-05    1.89639e-04      2017-03-27 08:15:07
  # DA47     1.32879e-04    7.39910e-05   -8.67609e-05    1.75097e-04      2017-03-27 08:15:07
  # DV16     2.33115e-05    1.64894e-04    2.70651e-05    1.68719e-04      2017-03-27 08:15:07
  # DV08     3.63952e-05   -1.39949e-04   -6.12251e-05    1.57031e-04      2017-03-27 08:15:07
  # DA46     1.69917e-06    1.51697e-04    3.40466e-05    1.55480e-04      2017-03-27 08:15:07
  # DV23    -7.98581e-05    5.53597e-05    1.16870e-04    1.51989e-04      2017-03-27 08:15:07
  # DV14    -6.47395e-05    6.25374e-05   -1.05502e-04    1.38682e-04      2017-03-27 08:15:07
  # DA48    -1.60115e-05    1.26317e-04   -1.10347e-05    1.27805e-04      2017-03-27 08:15:07
  # DV04     9.37773e-05    6.92129e-05   -3.67884e-05    1.22221e-04      2017-03-27 08:15:07
  # DA63    -7.55373e-05    9.48693e-05    1.22445e-05    1.21885e-04      2017-03-27 08:15:07
  # DV06     7.51251e-06    7.38157e-05    8.89474e-05    1.15831e-04      2017-03-27 08:15:07
  # DA53     1.50203e-05    1.00634e-04    4.99528e-05    1.13349e-04      2017-03-27 08:15:07
  # DV24     7.18268e-05    2.77864e-05   -7.87771e-05    1.10168e-04      2017-03-27 08:15:07
  # DV18     6.82778e-05   -5.17441e-07    8.54919e-05    1.09412e-04      2017-03-27 08:15:07
  # DA49     9.56579e-06    9.01965e-05    2.93782e-05    9.53415e-05      2017-03-27 08:15:07
  # DV17     4.78101e-05   -5.94730e-06    7.90432e-05    9.25689e-05      2017-03-27 08:15:07
  # DV09    -7.09007e-05   -3.66932e-05    2.81944e-05    8.46653e-05      2017-03-27 08:15:07
  # DV05    -5.63888e-05   -7.58469e-06   -3.86476e-05    6.87812e-05      2017-03-27 08:15:07
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms', tsystable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    field = '0',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    field = '1',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J1516+1932 didn't have any Tsys measurement, so I used the one made on Arp220. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    field = '2',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    field = '3',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.tsys', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.wvr', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split') 
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.flagversions') 
  
  mstransform(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms',
    outputvis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    datacolumn = 'corrected',
    spw = '17,19,21,23',
    reindex = False,
    keepflags = True)
  
  

print("# Calibration")

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.listobs')
  listobs(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    listfile = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    mode = 'shadow',
    flagbackup = False)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    mode = 'manual',
    spw = '17:0~7;120~127,19:0~7;120~127,21:0~7;120~127,23:0~7;120~127',
    flagbackup = False)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  setjy(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    standard = 'manual',
    field = 'J1256-0547',
    fluxdensity = [3.88999203876, 0, 0, 0],
    spix = -0.462875152087,
    reffreq = '892.174187976GHz')
  
  # fluxDensityUncertainty = 0.172646909777
  # meanAge = 8.0
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ap_pre_bandpass',
    field = '0', # J1256-0547
    spw = '17:0~127,19:0~127,21:0~127,23:0~127',
    scan = '1,3',
    solint = 'int',
    refant = 'DV10',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ap_pre_bandpass', msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass',
    field = '0', # J1256-0547
    scan = '1,3',
    solint = 'inf',
    combine = 'scan',
    refant = 'DV10',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass', msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_int',
    field = '0~1', # J1256-0547,J1504+1029
    solint = 'int',
    refant = 'DV10',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_int', msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ampli_inf',
    field = '0~1', # J1256-0547,J1504+1029
    solint = 'inf',
    refant = 'DV10',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ampli_inf', msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.flux_inf',
    reference = '0') # J1256-0547
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_inf',
    field = '0~1', # J1256-0547,J1504+1029
    solint = 'inf',
    refant = 'DV10',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_inf', msName='uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  for i in ['0']: # J1256-0547
    applycal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_int', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = True,
      flagbackup = False)
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    field = '1,2~3', # J1516+1932,Arp220
    gaintable = ['uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.bandpass', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.phase_inf', 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.flux_inf'],
    gainfield = ['', '1', '1'], # J1504+1029
    interp = 'linear,linear',
    calwt = True,
    flagbackup = False)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.cal') 
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#AMBIENT',
   'CALIBRATE_WVR#HOT',
   'CALIBRATE_WVR#OFF_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_CHECK_SOURCE#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  mstransform(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split',
    outputvis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = True)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  
stop = time.time()
count_time(stop, start)
