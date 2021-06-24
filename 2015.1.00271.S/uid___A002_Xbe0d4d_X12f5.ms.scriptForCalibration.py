# ALMA Data Reduction Script

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
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.
import analysisUtils as aU

import re

import os

if applyonly != True: es = aU.stuffForScienceDataReduction() 


if re.search('^4.7.0', casadef.casa_version) == None:
 sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 4.7.0')


# CALIBRATE_AMPLI: 
# CALIBRATE_ATMOSPHERE: Arp220,J1256-0547,J1504+1029
# CALIBRATE_BANDPASS: J1256-0547
# CALIBRATE_FLUX: J1256-0547
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J1504+1029
# CALIBRATE_POINTING: J1256-0547,J1504+1029
# OBSERVE_CHECK: J1516+1932
# OBSERVE_TARGET: Arp220

# Using reference antenna = DA59

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_Xbe0d4d_X12f5.ms') == False:
    importasdm('uid___A002_Xbe0d4d_X12f5', 
    asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', 
    bdfflags=True, lazy=False, process_caldevice=False)
    if not os.path.exists('uid___A002_Xbe0d4d_X12f5.ms.flagversions'):
      print 'ERROR in importasdm. Output MS is probably not useful. Will stop here.'
      thesteps = []
  if applyonly != True: es.fixForCSV2555('uid___A002_Xbe0d4d_X12f5.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xbe0d4d_X12f5.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.listobs')
  listobs(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    listfile = 'uid___A002_Xbe0d4d_X12f5.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    mode = 'manual',
    spw = '5~12,17~24',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xbe0d4d_X12f5.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xbe0d4d_X12f5.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.wvr',
    spw = [17, 19, 21, 23],
    toffset = 0,
    tie = ['J1516+1932,J1504+1029', 'Arp220,J1504+1029'],
    statsource = 'Arp220')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: 
    aU.plotWVRSolutions(caltable='uid___A002_Xbe0d4d_X12f5.ms.wvr', 
        spw='17', antenna='DA59', yrange=[-199,199],subplot=22, 
        interactive=False,
        figfile='uid___A002_Xbe0d4d_X12f5.ms.wvr.plots/uid___A002_Xbe0d4d_X12f5.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.tsys') 
  gencal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = F)
  
  # flag bad tsys: 
  # DA43: XX
  # DV 10: spw17: 07:49, spw 19: 08:08, spw 21: 08:08, spw23: 08:13, 08:15
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    mode = 'manual',
    antenna = 'DA43',
    spw = '',
    correlation = 'XX',
    flagbackup= F)
    
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    mode = 'manual',
    antenna = 'DV10',
    spw = '17',
    scan = '2,5,18',
    correlation = 'XX',
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    mode = 'manual',
    antenna = 'DV10',
    spw = '19',
    scan = '2',
    correlation = 'XX',
    flagbackup = F)
    
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    mode = 'manual',
    antenna = 'DV10',
    spw = '21',
    scan = '2,16,32',
    correlation = 'XX',
    flagbackup = F)

  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.tsys',
    mode = 'manual',
    antenna = 'DV10',
    spw = '23',
    scan = '2,18,20',
    correlation = 'XX',
    flagbackup = F)
  
  if applyonly != True: 
    aU.plotbandpass(caltable='uid___A002_Xbe0d4d_X12f5.ms.tsys', 
        overlay='time', xaxis='freq', yaxis='amp', subplot=22, 
        buildpdf=False, interactive=False, showatm=True,pwv='auto',chanrange='92.1875%', 
        showfdm=True, showBasebandNumber=True, showimage=True, 
        field='', 
        figfile='uid___A002_Xbe0d4d_X12f5.ms.tsys.plots.overlayTime/uid___A002_Xbe0d4d_X12f5.ms.tsys') 
    
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.tsys', 
        msName='uid___A002_Xbe0d4d_X12f5.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Position for antenna DA64 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DA61 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DA60 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV11 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: the correction for antenna DA44 is larger than 2mm.
  
  # Position for antenna DA44 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: no baseline run found for antenna DA47.
  
  # Note: no baseline run found for antenna DA41.
  
  # Position for antenna DA43 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV23 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV25 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: no baseline run found for antenna DA62.
  
  # Position for antenna DV08 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV09 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: no baseline run found for antenna DV19.
  
  # Position for antenna DV22 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: no baseline run found for antenna DV04.
  
  # Position for antenna DA50 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DA56 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DA54 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Note: no baseline run found for antenna DA55.
  
  # Position for antenna DV06 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DA58 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV03 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV13 is derived from baseline run made on 2017-03-19 07:39:48.
  
  # Position for antenna DV05 is derived from baseline run made on 2017-03-19 07:39:48.
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.antpos') 
  gencal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA43,DA44,DA50,DA54,DA56,DA58,DA60,DA61,DA64,DV03,DV05,DV06,DV08,DV09,DV11,DV13,DV22,DV23,DV25',
    #parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [-4.90042e-04,1.02638e-03,8.22466e-04,-5.16732e-04,1.91053e-03,8.27067e-04,-3.02855e-04,1.75168e-04,9.51592e-05,-2.82780e-04,5.09117e-04,1.70356e-04,-1.58749e-04,2.29643e-04,9.83031e-06,-1.76075e-04,2.89783e-05,-1.00558e-04,-1.53140e-04,4.56306e-04,1.45270e-04,3.63089e-05,3.78767e-04,1.99747e-04,-1.49663e-04,1.86292e-04,1.53141e-05,1.70628e-04,-3.08856e-04,4.84945e-05,-9.29328e-05,-2.95802e-04,-5.19009e-05,8.34641e-06,-1.07577e-04,4.02064e-05,4.06274e-05,-3.68755e-04,6.32327e-05,-1.11344e-04,-2.03245e-04,-3.99223e-05,-7.10332e-05,-3.94258e-04,-3.22901e-04,2.93692e-05,2.24042e-04,4.04162e-04,-1.62585e-04,-1.25512e-04,8.18620e-07,-1.65932e-04,1.01913e-04,2.62822e-04,-2.43497e-04,8.22497e-04,2.61589e-04])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DA44    -5.16732e-04    1.91053e-03    8.27067e-04    2.14504e-03      2017-03-19 07:39:48
  # DA43    -4.90042e-04    1.02638e-03    8.22466e-04    1.40358e-03      2017-03-19 07:39:48
  # DV25    -2.43497e-04    8.22497e-04    2.61589e-04    8.96784e-04      2017-03-19 07:39:48
  # DA54    -2.82780e-04    5.09117e-04    1.70356e-04    6.06783e-04      2017-03-19 07:39:48
  # DV11    -7.10332e-05   -3.94258e-04   -3.22901e-04    5.14539e-04      2017-03-19 07:39:48
  # DA60    -1.53140e-04    4.56306e-04    1.45270e-04    5.02763e-04      2017-03-19 07:39:48
  # DV13     2.93692e-05    2.24042e-04    4.04162e-04    4.63038e-04      2017-03-19 07:39:48
  # DA61     3.63089e-05    3.78767e-04    1.99747e-04    4.29746e-04      2017-03-19 07:39:48
  # DV08     4.06274e-05   -3.68755e-04    6.32327e-05    3.76336e-04      2017-03-19 07:39:48
  # DA50    -3.02855e-04    1.75168e-04    9.51592e-05    3.62574e-04      2017-03-19 07:39:48
  # DV03     1.70628e-04   -3.08856e-04    4.84945e-05    3.56171e-04      2017-03-19 07:39:48
  # DV23    -1.65932e-04    1.01913e-04    2.62822e-04    3.27101e-04      2017-03-19 07:39:48
  # DV05    -9.29328e-05   -2.95802e-04   -5.19009e-05    3.14371e-04      2017-03-19 07:39:48
  # DA56    -1.58749e-04    2.29643e-04    9.83031e-06    2.79346e-04      2017-03-19 07:39:48
  # DA64    -1.49663e-04    1.86292e-04    1.53141e-05    2.39454e-04      2017-03-19 07:39:48
  # DV09    -1.11344e-04   -2.03245e-04   -3.99223e-05    2.35160e-04      2017-03-19 07:39:48
  # DV22    -1.62585e-04   -1.25512e-04    8.18620e-07    2.05397e-04      2017-03-19 07:39:48
  # DA58    -1.76075e-04    2.89783e-05   -1.00558e-04    2.04827e-04      2017-03-19 07:39:48
  # DV06     8.34641e-06   -1.07577e-04    4.02064e-05    1.15148e-04      2017-03-19 07:39:48
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xbe0d4d_X12f5.ms', tsystable = 'uid___A002_Xbe0d4d_X12f5.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    field = '0',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5.ms.tsys', 'uid___A002_Xbe0d4d_X12f5.ms.wvr', 'uid___A002_Xbe0d4d_X12f5.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    field = '1',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5.ms.tsys', 'uid___A002_Xbe0d4d_X12f5.ms.wvr', 'uid___A002_Xbe0d4d_X12f5.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  # Note: J1516+1932 didn't have any Tsys measurement, so I used the one made on Arp220. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    field = '2',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5.ms.tsys', 'uid___A002_Xbe0d4d_X12f5.ms.wvr', 'uid___A002_Xbe0d4d_X12f5.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    field = '3',
    spw = '17,19,21,23',
    gaintable = ['uid___A002_Xbe0d4d_X12f5.ms.tsys', 'uid___A002_Xbe0d4d_X12f5.ms.wvr', 'uid___A002_Xbe0d4d_X12f5.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xbe0d4d_X12f5.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split*') 
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.flagversions') 
  
  split(vis = 'uid___A002_Xbe0d4d_X12f5.ms',
    outputvis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    datacolumn = 'corrected',
    spw = '17,19,21,23',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.listobs')
  listobs(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    listfile = 'uid___A002_Xbe0d4d_X12f5.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xbe0d4d_X12f5.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127,3:0~7;120~127',
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  #
  # Check the calibrator
  #

  #aU.getALMAFlux('J1256-0547', '892.17487976GHz', 
  #    date='20170318')
  #  {'ageDifference': 9.0,
  #   'fluxDensity': 5.4247392272357216,
  #   'fluxDensityUncertainty': 0.40118555311096871,
  #   'meanAge': 5.666666666666667,
  #   'monteCarloFluxDensity': 5.3504473671287016,
  #   'spectralIndex': -0.31835425856185917,
  #   'spectralIndexUncertainty': 0.0068348635061699315}

  setjy(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    standard = 'manual',
    field = 'J1256-0547',
    fluxdensity = [5.42474056633, 0, 0, 0],
    spix = -0.318354258562,
    reffreq = '892.174187976GHz')
  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.ap_pre_bandpass') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.ap_pre_bandpass',
    field = '0', # J1256-0547
    spw = '0:32~97,1:32~97,2:32~97,3:32~97',
    scan = '1,3',
    solint = 'int',
    refant = 'DA59',
    calmode = 'p')
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.ap_pre_bandpass',
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  #
  # Normal bandpass
  #
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass',
    field = '0', # J1256-0547
    scan = '1,3',
    solint = 'inf, 2.3MHz',
    combine = 'scan',
    refant = 'DA59',
    solnorm = True,
    bandtype = 'B',
    minsnr  = 2.0,
    gaintable = 'uid___A002_Xbe0d4d_X12f5.ms.split.ap_pre_bandpass')
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.bandpass', 
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  #
  # Smoothed bandpass
  #
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth') 
  bandpass(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth',
    field = '0', # J1256-0547
    scan = '1,3',
    solint = 'inf, 6.1MHz',
    combine = 'scan',
    refant = 'DA59',
    solnorm = True,
    bandtype = 'B',
    minsnr = 2.0,
    gaintable = 'uid___A002_Xbe0d4d_X12f5.ms.split.ap_pre_bandpass')
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth', 
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  #
  # Phase diff first
  #
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff',
    field = '0', # J1256-0547,J1504+1029,J1516+1932
    solint = 'inf',
    refant = 'DA59',
    gaintype = 'G',
    calmode = 'p',
    combine = 'scan',
    gaintable = 'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth')
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff', 
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  
  #
  # Phase cal with more than int to get higher s/n
  #
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.phase_int.*') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.phase_int',
    field = '0~2', # J1256-0547,J1504+1029,J1516+1932
    solint = '25.3s',
    refant = 'DA59',
    gaintype = 'G',
    calmode = 'p',
    combine = 'spw',
    minsnr = 2.5,
    gaintable = [ 
            'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth',
           'uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff'])
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.phase_int', 
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  #
  # Ampli cal
  #
  print 'Calibrating amplitude'
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.ampli_inf',
    field = '0~2', # J1256-0547,J1504+1029,J1516+1932
    solint = 'inf',
    refant = 'DA59',
    gaintype = 'T',
    calmode = 'a',
    combine = 'spw',
    spwmap = [[],[],[0,0,0,0]],
    gaintable = [
        'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth',   
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff',
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_int'])
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.ampli_inf',     
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xbe0d4d_X12f5.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xbe0d4d_X12f5.ms.split.flux_inf',
    reference = '0') # J1256-0547
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: 
    es.fluxscale2(caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.ampli_inf', 
        removeOutliers=True, msName='uid___A002_Xbe0d4d_X12f5.ms', 
        writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    caltable = 'uid___A002_Xbe0d4d_X12f5.ms.split.phase_inf',
    field = '0~2', # J1256-0547,J1504+1029,J1516+1932
    solint = 'inf',
    refant = 'DA59',
    gaintype = 'G',
    calmode = 'p',
    combine = 'spw',
    gaintable = [
        'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth',
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff'])
  
  if applyonly != True: 
    es.checkCalTable('uid___A002_Xbe0d4d_X12f5.ms.split.phase_inf',
        msName='uid___A002_Xbe0d4d_X12f5.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # J1256-0547
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    field = str(0),
    gaintable = [
        'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth',
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff',
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_int',
        'uid___A002_Xbe0d4d_X12f5.ms.split.flux_inf'],
    spwmap = [[],[],[0,0,0,0],[0,0,0,0]],
    gainfield = ['0', '0', '0','0'],
    interp = ['linear','linear','linear','linear'],
    calwt = T,
    flagbackup = F)
  #
  # Apply to the rest
  #
  applycal(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    field = '1,2~3', # J1516+1932,Arp220
    gaintable = [
        'uid___A002_Xbe0d4d_X12f5.ms.split.bandpass_smooth',
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_diff',
        'uid___A002_Xbe0d4d_X12f5.ms.split.phase_inf',
        'uid___A002_Xbe0d4d_X12f5.ms.split.flux_inf'],
    gainfield = ['0','0', '1', '1'], # J1504+1029
    interp =['','','linearPD',''],
    spwmap = [[],[],[0,0,0,0],[0,0,0,0]],
    calwt = T,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.cal') 
  os.system('rm -rf uid___A002_Xbe0d4d_X12f5.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#AMBIENT',
   'CALIBRATE_WVR#HOT',
   'CALIBRATE_WVR#OFF_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_CHECK_SOURCE#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  split(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split',
    outputvis = 'uid___A002_Xbe0d4d_X12f5.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = T)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xbe0d4d_X12f5.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  
stop = time.time()
count_time(stop, start)
