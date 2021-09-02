import numpy as np
import matplotlib.pyplot as plt

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

print vis

###########################################################
# functions
def regrid_time(xdata, ydata, xtime, ytime):
    '''
    ------
    paramters:
    xdata: np.ndarray.
        array of data to be synchronized to
    ydata: np.ndarray
        array of data to be synchronized
    xtime: np.ndarray.
        array of time the xdata is taken
    ytime: np.ndarray.
        array of time the ydata is taken
    ------
    retrun: 
    ydata_regridded: np.array
        regridded ydata with same shape as xdata
    '''  
    ydata_regridded = np.full(np.shape(xdata), np.nan)
    
    # match the xtime with ytime 
    dist = np.abs(ytime[:, np.newaxis] - xtime)
    potentialClosest = dist.argmin(axis=1)
    closestFound, closestCounts = np.unique(potentialClosest, return_counts=True)
    ydata_group = np.split(ydata, np.cumsum(closestCounts)[:-1])
    
    # leave out the time with spacing greater than the interval of original time.
       

    for i, index in enumerate(closestFound):
        ydata_regridded[index] = np.nanmean(ydata_group[i])
  
    return ydata_regridded

###########################################################
# tb.open(vis+'/ANTENNA')
# tb2=tb.getcol('NAME')
# 
# 
# # measure the system temperature
# nant=1
# for iant in range(nant):
#     tb.open(vis+'/SYSCAL')
#     tb3 = tb.query('ANTENNA_ID==%d'%(iant))
#     Tsys_spectrum = tb3.getcol('TSYS_SPECTRUM')
#     tb.close()
# 
# ddid = 0     # number equivalent of spectral window. this may be found in the browsetable
#              # spectral window number
# 
# # measure the hot load and cold load
# Tambs = []
# Thots = []
# for iant in range(nant):
# #    pl.clf()
#     Tfss = []
#     tb.open(vis+'/CALDEVICE')
#     tb0=tb.query('ANTENNA_ID==%d'%(iant)) 
#     temps = tb0.getcol('TEMPERATURE_LOAD')
#     Tambs.append(np.mean(temps[0]))
#     Thots.append(np.mean(temps[1]))
# 
#     for ddid in range(0,4):
#         this_ant = tb2[iant]
# 
# # Get the time and pointing
# tb.open(vis+'/POINTING') 
# tb1=tb.query('ANTENNA_ID==%d'%(iant))
# dd=tb1.getcol('DIRECTION')
# tt=np.array(tb1.getcol('TIME'))
# 
# en=tb1.getcol('ENCODER')
# el = en[1]*57.29

# Get the actual data 
tb.open(vis)

# test for antenna 0
iant = 0 

# only need to worry about autocorrelation, haven't considered cross-correlation yet.
scan_ATM = [2,5,8,10, 12, 16,18, 20, 24, 26, 28, 32, 34]

## get the SQLD data. 
spw_SQLD = [13,14,15,16]
# ddid = spw_SQLD; ddid2=13
# 0, 1, 2, 3 is for the pointing
dat = tb.query("ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID in %s && SCAN_NUMBER not in %s"%(iant,iant, spw_SQLD, scan_ATM)) # 2 is scan id
sig = np.real(dat.getcol('DATA'))
sig_avg = np.mean(sig, axis=(0,1))
sig_time=dat.getcol('TIME')

## get the WVR data
spw_WVR = 4
ddid = spw_WVR
dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID==%d'%(iant,iant,ddid))
WVR = np.real(dat.getcol('DATA'))
WVR_avg = np.mean(WVR, axis=(0,1)) 
chan_WVR = 0
WVR_chan = WVR[0][chan_WVR]
WVR_time = dat.getcol('TIME')

## Get the autocorrelation data
spw_autCorr = [18,20,22,24] # 6, 8, 10, 12 is for the pointing
spw_autCorr = [18]
ddid = spw_autCorr
dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID in %s && SCAN_NUMBER not in %s'%(iant,iant,spw_autCorr, scan_ATM))
AutCorr = np.real(dat.getcol('DATA'))
AutCorr_avg = np.mean(AutCorr, axis=(0,1))
AutCorr_time = dat.getcol('TIME')

### Synchronize time
# WVR has larger range, SQLD and chan_avg have the same range
# SQLD has the shortest interval, WVR and chan_avg interval are similiar (1 sec)

## match the autocorrleation and SQLD with WVR

xdata = WVR_chan; xtime = WVR_time
ydata = AutCorr_avg; ytime = AutCorr_time
AutCorr_regridded = regrid_time(xdata, ydata, xtime, ytime)

xdata = WVR_avg; xtime = WVR_time
ydata = sig_avg; ytime = sig_time 
sig_regridded = regrid_time(xdata, ydata, xtime, ytime)

# plot WVR vs autocorrelation
fig = plt.figure()
plt.title('Ant '+str(iant)+', WVR chan '+str(chan_WVR)+', autocorrelation spw '+str(spw_autCorr))
plt.scatter(WVR_chan, AutCorr_regridded)
plt.xlabel('WVR data')
plt.ylabel('Autocorrelation data')
plt.savefig('WVR_autocorrelation_ant'+str(iant)+'_chanWVR'+str(chan_WVR)+'_spwAutCorr'+str(spw_autCorr)+'.pdf',
            bbox_inches='tight')

# plot WVR vs SQRD
fig = plt.figure()
plt.title('Ant '+str(iant)+', WVR chan '+str(chan_WVR)+', SQLD spw '+str(spw_SQLD))
plt.scatter(WVR_chan, sig_regridded, marker='o')
plt.xlabel('WVR data')
plt.ylabel('SQLD data')
plt.savefig('WVR_SQLD_ant'+str(iant)+'_chanWVR'+str(chan_WVR)+'_spwSQLD'+str(spw_SQLD)+'.pdf',
            bbox_inches='tight')



## ddid for autocorrelation, WVR (Try different antennas, different WVR channels, WVR all scans, autocorrelation & SQLD same scan)
# Try WVR vs SQLD, take at the same time
# Try autocorrelation vs WVR, 
# ATM cal has different spws from science data
