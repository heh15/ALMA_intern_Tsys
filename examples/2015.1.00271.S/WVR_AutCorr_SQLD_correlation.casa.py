import numpy as np
import matplotlib.pyplot as plt

###########################################################
# basic information

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

# antenna number
iant = 10
pol = 0 # -1 means to average

# scan number for different types of the observation
scan_ATM = [2,5,8,10,12,16,18,20,24,26,28,32,34]
scan_phase = np.array([6,11,14,19,22,27,30,35])
scan_checksource = np.array([7, 15, 23, 31])
scan_bpass = np.array([3])
scan_sci = np.array([7,9,13,17,21,25,29,33])

# spectral window for different types of data
spws_SQLD = [13,14,15,16] # spw 0,1,2,3 is for the pointing
spw_SQLD = 14
spws_autCorr = [18,20,22,24] # 6, 8, 10, 12 is for the pointing
spw_autCorr = 18
spw_WVR = 4

# channel for WVR data
chan_WVR = 0

Global_title = ' Ant '+str(iant)
Global_filename = '_ant'+str(iant)

WVR_title = ', WVR chan '+str(chan_WVR)
WVR_filename = '_chanWVR'+str(chan_WVR)

AutCorr_title = ', AutCorr spw '+str(spw_autCorr)+', AutCorr pol '+str(pol)
AutCorr_filename = '_spwAutCorr'+str(spw_autCorr)+'_polAutCorr'+str(pol)

SQLD_title=', SQLD spw '+str(spw_SQLD)+', SQLD pol '+str(pol)
SQLD_filename = '_spwSQLD'+str(spw_SQLD)+'_polSQLD'+str(pol)

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

def average_spws(vis, spws, iant=0, spw_template=None):
    '''
    Average data among different spectral windows
    ------
    Parameters:
    vis: str
        Path to the measurement set 
    spws: list
        List of spectral windows
    iant: int
        The ID of the antennae
    spw_template: float
        One of the spectral windows all the other will be regridded to
    ------
    Return:
    data_avg: np.ndarray
        data that averaged among different spws
    time: np.ndarray
        time corresonding to averaged data 
    '''
    # read table 
    tb.open(vis)

    # initalize variables
    if spw_template == None:
        spw_template = spws[0]
    Table = {}

    for i in spws:
        data_label = 'spw '+str(i)+' data'
        time_label = 'spw '+str(i)+' time'
        dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID ==%d && SCAN_NUMBER not in %s'%(iant,iant,i, scan_ATM))
        data = np.mean(np.real(dat.getcol('DATA')), axis=(0,1))
        time = dat.getcol('TIME')
        Table[data_label] = data
        Table[time_label] = time

    tb.close()
    # regrid the data to the time of the first data
    data_columns = []
    for i in spws:
        data_label = 'spw '+str(i)+' data'
        time_label = 'spw '+str(i)+' time'
        regrid_label = 'spw '+str(i)+' regridded'
        data_template = 'spw '+str(spw_template)+' data'
        time_template = 'spw '+str(spw_template)+' time'
        Table[regrid_label] = regrid_time(Table[data_template], Table[data_label],
                                          Table[time_template], Table[time_label])
        data_columns.append(regrid_label)

    # average the data in different spectral windows
    time = np.array(Table[time_template])
    data_avg = np.full((len(data_columns), len(time)), np.nan)
    for i, column in enumerate(data_columns):
        data_avg[i] = Table[column]
    data_avg = np.mean(data_avg, axis=0)

    return data_avg, time

###########################################################
# main program

#############################
# get the data

## get the SQLD data 
tb.open(vis)
ddid = spw_SQLD
# exclude the scan in ATM cal. 
dat = tb.query("ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID in %s && SCAN_NUMBER not in %s"%(iant,iant,ddid, list(scan_ATM))) # 2 is scan id
sig = np.real(dat.getcol('DATA'))
if pol == -1:
    sig_sinspw = np.mean(sig, axis=(0,1))
else:
    sig_sinspw = sig[pol][0]
sig_time=dat.getcol('TIME')
tb.close()

# # average different spectral windows
# spws = spws_SQLD
# sig_avg2, sig_time2 = average_spws(vis, spws, iant=iant)

## get the WVR data
ddid = spw_WVR
tb.open(vis)
dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID==%d'%(iant,iant,ddid))
WVR = np.real(dat.getcol('DATA'))
WVR_avg = np.mean(WVR, axis=(0,1)) 
WVR_sinchan = WVR[0][chan_WVR]
WVR_time = dat.getcol('TIME')
tb.close()

# exclude the WVR data with hot load
WVR_sinchan[WVR_sinchan > 200] = np.nan
WVR_avg[WVR_avg > 200] = np.nan

## Get the autocorrelation data
ddid = spw_autCorr
tb.open(vis)
dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID in %s && SCAN_NUMBER not in %s'%(iant,iant,ddid,scan_ATM))
AutCorr = np.real(dat.getcol('DATA'))
if pol == -1:
    AutCorr_sinspw = np.mean(AutCorr, axis=(0,1))
else:
    AutCorr_sinspw = AutCorr[pol][0]
AutCorr_time = dat.getcol('TIME')
tb.close()

# get the average data, AutCorr_avg doesn't average over different spws. 
spws = spws_autCorr
AutCorr_avg2, AutCorr_time2 = average_spws(vis, spws, iant=iant)

#############################
# Synchronize time

# WVR has larger range, SQLD and chan_avg have the same range
# SQLD has the shortest interval, WVR and chan_avg interval are similiar (1 sec)

## match the autocorrleation and SQLD with WVR

xdata = WVR_avg; xtime = WVR_time
ydata = AutCorr_sinspw; ytime = AutCorr_time
AutCorr_regridded = regrid_time(xdata, ydata, xtime, ytime)

xdata = WVR_avg; xtime = WVR_time
ydata = AutCorr_avg2; ytime = AutCorr_time2
AutCorr_regridded2 = regrid_time(xdata, ydata, xtime, ytime)

xdata = WVR_avg; xtime = WVR_time
ydata = sig_sinspw; ytime = sig_time
sig_regridded = regrid_time(xdata, ydata, xtime, ytime)

## match the SQLD with autocorrelation
xdata = AutCorr_avg2; xtime = AutCorr_time2
ydata = sig_sinspw; ytime = sig_time
sig_regridded2 = regrid_time(xdata, ydata, xtime, ytime)

##############################
# plot the correlation

##  plot WVR vs autocorrelation
xdata = WVR_avg; ydata = AutCorr_regridded
spw_Ytext = str(spw_autCorr)
chan_Xtext = str(chan_WVR)
chan_Xtext = 'avg'

fig = plt.figure()
plt.title(Global_title+WVR_title+AutCorr_title)
plt.scatter(xdata, ydata)

# fit the correlation
idx_nnan = ((~np.isnan(xdata)) & (~np.isnan(ydata)))
fit_results = np.polyfit(xdata[idx_nnan], ydata[idx_nnan], 1, full=True)
fit_coeff = fit_results[0]
fit_err = fit_results[1]
ydata_fitted = fit_coeff[0] * xdata + fit_coeff[1]
plt.plot(xdata, ydata_fitted, color='black', linestyle='dotted',
        label=str(round(fit_coeff[0], 4))+'*x+'+str(round(fit_coeff[1], 4))
        +'\n err: '+str(round(fit_err[0], 4)))

x = xdata[idx_nnan, np.newaxis]
fit_results = np.linalg.lstsq(x, ydata[idx_nnan])
fit_coeff1 = fit_results[0]
fit_err1 = fit_results[1]
ydata_fitted1 = fit_coeff1[0] * xdata
plt.plot(xdata, ydata_fitted1, color='red', linestyle='dotted', 
        label=str(round(fit_coeff1[0], 4))+'*x+'
        +'\n err: '+str(round(fit_err1[0], 4)))

plt.xlabel('WVR data')
plt.ylabel('Autocorrelation data')
plt.legend()
plt.savefig('WVR_autocorrelation'+Global_filename+WVR_filename+AutCorr_filename+'.pdf')

##  plot WVR vs SQLD
# input for the figure
xdata = WVR_sinchan; ydata = sig_regridded
spw_Ytext = str(spw_SQLD)
chan_Xtext = str(chan_WVR)

fig = plt.figure()
plt.title(Global_title+WVR_title+SQLD_title)
plt.scatter(WVR_sinchan, sig_regridded, marker='o')

# fit the correlation
idx_nnan = ((~np.isnan(xdata)) & (~np.isnan(ydata)))
fit_results = np.polyfit(xdata[idx_nnan], ydata[idx_nnan], 1, full=True)
fit_coeff = fit_results[0]
fit_err = fit_results[1]
ydata_fitted = fit_coeff[0] * xdata + fit_coeff[1]
plt.plot(xdata, ydata_fitted, color='black', linestyle='dotted',
        label=str(round(fit_coeff[0], 6))+'*x+'+str(round(fit_coeff[1], 4))
        +'\n err: '+str(round(fit_err[0], 6)))

x = xdata[idx_nnan, np.newaxis]
fit_results = np.linalg.lstsq(x, ydata[idx_nnan])
fit_coeff1 = fit_results[0]
fit_err1 = fit_results[1]
ydata_fitted1 = fit_coeff1[0] * xdata
plt.plot(xdata, ydata_fitted1, color='red', linestyle='dotted',
        label=str(round(fit_coeff1[0], 6))+'*x+'
        +'\n err: '+str(round(fit_err1[0], 6)))
plt.legend()

# label the data
plt.xlabel('WVR data')
plt.ylabel('SQLD data')
fig.tight_layout()
plt.savefig('WVR_SQLD'+Global_filename+WVR_filename+SQLD_filename+'.pdf',
            bbox_inches='tight')


## plot the SQLD vs autocorrelation
# input for the figure
xdata = AutCorr_sinspw; ydata = sig_regridded2
spw_Ytext = str(spw_SQLD)
spw_Xtext = str(spw_autCorr)

fig = plt.figure()
plt.title(Global_title+AutCorr_title+SQLD_title)
plt.scatter(xdata, ydata, marker='o')

# fit the correlation
idx_nnan = ((~np.isnan(xdata)) & (~np.isnan(ydata)))
fit_results = np.polyfit(xdata[idx_nnan], ydata[idx_nnan], 1, full=True)
fit_coeff = fit_results[0]
fit_err = fit_results[1]
ydata_fitted = fit_coeff[0] * xdata + fit_coeff[1]
plt.plot(xdata, ydata_fitted, color='black', linestyle='dotted',
        label=str(round(fit_coeff[0], 6))+'*x+'+str(round(fit_coeff[1], 6))
        +'\n err: '+str(round(fit_err[0], 6)))

x = xdata[idx_nnan, np.newaxis]
fit_results = np.linalg.lstsq(x, ydata[idx_nnan])
fit_coeff1 = fit_results[0]
fit_err1 = fit_results[1]
ydata_fitted1 = fit_coeff1[0] * xdata
plt.plot(xdata, ydata_fitted1, color='red', linestyle='dotted',
        label=str(round(fit_coeff1[0], 6))+'*x+'
        +'\n err: '+str(round(fit_err1[0], 6)))
plt.legend()

# label the data
plt.xlabel('Autcorr data')
plt.ylabel('SQLD data')
fig.tight_layout()
plt.savefig('AutCorr_SQLD'+Global_filename+AutCorr_filename+SQLD_filename+'.pdf',
            bbox_inches='tight')

## ddid for autocorrelation, WVR (Try different antennas, different WVR channels, WVR all scans, autocorrelation & SQLD same scan)
# Try WVR vs SQLD, take at the same time
# Try autocorrelation vs WVR, 
# ATM cal has different spws from science data
