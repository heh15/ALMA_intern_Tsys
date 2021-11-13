import numpy as np
import matplotlib.pyplot as plt

###########################################################
# basic parameters

vis = 'uid___A002_Xbf792a_X14cc.ms'

iant = 10 # antenna id
chan_WVR = -1 # WVR channels

spw_Tsys = 17 # Tsys spectral window
average_spw = True
if average_spw == False:
    spw_Tsys = 'avg'

# scan id 
msmd.open(vis)
scan_ATM = msmd.scansforintent('*CALIBRATE_ATMOSPHERE*')
scan_phase = msmd.scansforintent('*CALIBRATE_PHASE*')
scan_checksource = msmd.scansforintent('*OBSERVE_CHECK_SOURCE*')
scan_bpass = msmd.scansforintent('*CALIBRATE_BANDPASS*')
scan_sci = msmd.scansforintent('*OBSERVE_TARGET*')
msmd.done()

# spectral window
spws_autCorr = [18,20,22,24]
spw_autCorr = 18

# normalized scans
scinormScan  = 0
phasenormScan = 0
bpassnormScan = 0

normScans = [phasenormScan, scinormScan, bpassnormScan]

# Tsys and Tsky
keywords_title = ' Ant '+str(iant)+' WVR chan '+str(chan_WVR)+' Tsys spw '+str(spw_Tsys)
keywords_filename = '_ant'+str(iant)+'_chanWVR'+str(chan_WVR)+'_Tsys_spw'+str(spw_Tsys)

###########################################################
# functions

def find_nearest(array, values):
    '''
    Find the index of the values in the array closest to the given value
    ------
    Parameters:
    array: numpy.ndarray
        numpy array to be matched
    values: numpy.ndarray or float64
        values to be matched with numpy array
    ------
    Return:
    idx: int
        index of the closest value in array.
    '''
    array = np.asarray(array)
    idx = np.nanargmin((np.abs(array[:,np.newaxis] - values)), axis=0)

    return idx


def array_isin(element, test_elements):

    dist = np.abs(element[:, np.newaxis] - test_elements)
    diff = np.nanmin(dist, axis=1)
    isin = np.where(diff == 0)

    return isin

def average_Tsys(Tsys_spectrum, chan_trim=5, average_spw=False, spws=[]):

    Tsys_avg1 = np.mean(Tsys_spectrum, axis=0)
    Tsys_avg2 = Tsys_avg1[chan_trim: (len(Tsys_avg1)-chan_trim)]
    Tsys = np.mean(Tsys_avg2, axis=0)

    if (average_spw == True) and len(spws) != 0:
        spw_unique = np.unique(spws)
        shape = (len(spw_unique), int(len(Tsys)/len(spw_unique)))
        Tsys_temp = np.full(shape, np.nan)
        for i, spw in enumerate(np.unique(spws)):
            Tsys_temp[i] = Tsys[np.where(spws==spw)]

        Tsys = np.mean(Tsys_temp, axis=0)

    return Tsys

def select_spw_Tsys(Tsys, spws, spwid):

    Tsys_sinspw = Tsys[np.where(spws==spwid)]

    return Tsys_sinspw


def normalize_Tsys(Tsys_sinspw, isin_phase, isin_sci, isin_bpass):

    Tsys_norm = np.full(np.shape(Tsys_sinspw), np.nan)
    isins = [isin_phase, isin_sci, isin_bpass]

    for isin in isins:
        if len(isin[0]) == 0:
            continue
        else:
            Tsys_norm[isin] = Tsys_sinspw[isin] / Tsys_sinspw[isin[0][0]]

    return Tsys_norm

def normalize_array(array, iants, obs_type):

    array_norm = np.full(np.shape(array), fill_value=np.nan)
    iants_uq = np.unique(iants)
    obsType_uq = np.unique(obs_type)
    for iant in iants_uq:
        for obs in obsType_uq:
            conditions = ((iants == iant) & (obs_type==obs))
            indices = np.where(conditions)
            array_sub = array[indices]
            array_norm[indices] = array_sub / array_sub[0]

    return array_norm

def map_series_by_dict(a, d):

    v = np.array(list(d.values()))
    k = np.array(list(d.keys()))
    sidx = k.argsort()
    out_ar = v[sidx[np.searchsorted(k,a,sorter=sidx)]]
    return out_ar


###########################################################
# main program

############################# 
# read the WVR data 
tb.open(vis)
spw_WVR = 4
ddid = spw_WVR
scan_exclude = list(scan_checksource)
dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID==%d && SCAN_NUMBER not in %s'%(iant,iant,ddid,scan_exclude))
WVR = np.real(dat.getcol('DATA'))
WVR_avg = np.mean(WVR, axis=(0,1))
WVR_time = dat.getcol('TIME')
WVR_scans = dat.getcol('SCAN_NUMBER')
tb.close()

## exclude the hot and cold load in the WVR measurement
WVR_time[np.where(WVR[0][3]>200)] = np.nan
WVR[np.where(WVR > 200)] = np.nan

## average the 4 different WVR channels with the weighting
if chan_WVR == -1:
    weights = WVR[0]/275 * (WVR[0]/275-1)
    WVR_sinchan = np.average(WVR[0], axis=0, weights=weights)
else:
    WVR_sinchan = WVR[0][chan_WVR]

## categorize WVR into different types observations
obsTypes_WVR = np.empty(np.shape(WVR_sinchan), dtype='S10')
obsTypes_WVR[:] = ' '

elements = WVR_scans

test_elements = np.array(list(scan_phase)+list(np.intersect1d((scan_phase-1), scan_ATM)))
isin_phase_WVR = array_isin(elements, test_elements)
obsTypes_WVR[isin_phase_WVR] = 'phase'

test_elements = np.array(list(scan_sci)+list(np.intersect1d((scan_sci-1), scan_ATM)))
isin_sci_WVR = array_isin(elements, test_elements)
obsTypes_WVR[isin_sci_WVR] = 'science'

test_elements = np.array(list(scan_bpass)+list(np.intersect1d((scan_bpass-1), scan_ATM)))
isin_bpass_WVR = array_isin(elements, test_elements)
obsTypes_WVR[isin_bpass_WVR] = 'bandpass'

isin_obsrs_WVR = [isin_phase_WVR, isin_sci_WVR, isin_bpass_WVR]

# convert it to string
obsTypes_WVR = obsTypes_WVR.astype('str')

#############################
# read the Tsys

# import the Tsys
tb.open(vis+'/SYSCAL')
tb3 = tb.query('ANTENNA_ID==%d'%(iant))
Tsys_spectrum = tb3.getcol('TSYS_SPECTRUM')
Trx_spectrum = tb3.getcol('TRX_SPECTRUM')
Tsky_spectrum = tb3.getcol('TSKY_SPECTRUM')
spws = tb3.getcol('SPECTRAL_WINDOW_ID')
time = tb3.getcol('TIME')
tb.close()

# average Tsys for two correlations and all spectral channels
Tsys = average_Tsys(Tsys_spectrum, average_spw=average_spw, spws=spws)
Trx = average_Tsys(Trx_spectrum, average_spw=average_spw, spws=spws)
Tsky = average_Tsys(Tsky_spectrum, average_spw=average_spw, spws=spws)

# select Tsys from a single spectral window
if average_spw == False:
    Tsys_sinspw = select_spw_Tsys(Tsys, spws, spw_Tsys)
    Trx_sinspw = select_spw_Tsys(Trx, spws, spw_Tsys)
    Tsky_sinspw = select_spw_Tsys(Tsky, spws, spw_Tsys)
else:
    Tsys_sinspw = Tsys
    Trx_sinspw = Trx
    Tsky_sinspw = Tsky

# import the Tsys time 
time_Tsys = []
msmd.open(vis)
for scan in scan_ATM:
    times = msmd.timesforscans(scan)
    times_range = [times[0], times[-1]]
    time_Tsys.append(times_range)
msmd.done()
time_Tsys = np.array(time_Tsys)
dur_Tsys = time_Tsys[:,-1] - time_Tsys[:,0]
time_Tsys_avg = np.mean(time_Tsys, axis=1)

# categorize Tsys into different types of observations
obs_type = np.empty(np.shape(scan_ATM),dtype="S10")
elements = scan_ATM + 1

test_elements = scan_sci
isin_sci = array_isin(elements, test_elements)
obs_type[isin_sci] = 'science'

test_elements = scan_phase
isin_phase = array_isin(elements, test_elements)
obs_type[isin_phase] = 'phase'

test_elements = scan_bpass
isin_bpass = array_isin(elements, test_elements)
obs_type[isin_bpass] = 'bandpass'


#############################
# extrapolate the WVR based on Tsys

Tsys_ext = np.full(np.shape(WVR_sinchan), fill_value=np.nan)
Tsky_ext = np.full(np.shape(WVR_sinchan), fill_value=np.nan)

isin_obsrs = [isin_phase, isin_sci, isin_bpass]
for i, isin_obs in enumerate(isin_obsrs):
    if len(isin_obs) !=0:
        WVR_time_obs = WVR_time[isin_obsrs_WVR[i]]
        WVR_obs = WVR_sinchan[isin_obsrs_WVR[i]]
        ind = find_nearest(WVR_time_obs, time_Tsys_avg[isin_obs])

        # match the start of Tsys
        Tsys_start = Tsys_sinspw[isin_obs][normScans[i]]
        Tsky_start = Tsky_sinspw[isin_obs][normScans[i]]
        WVR_start = WVR_obs[isin_obs][normScans[i]]
        Tsys_ext[isin_obsrs_WVR[i]] = Tsys_start * WVR_obs / WVR_start
        Tsky_ext[isin_obsrs_WVR[i]] = Tsky_start * WVR_obs / WVR_start


# match start of Tsys with the start of autocorrelation data
# sci_ind0 = find_nearest(WVR_time, time_Tsys_sci[:,-1][0])
# 
# exclude the WVRelation data at ATM scan
# WVR_avg[np.where(WVR_avg<0.5)] = np.nan
# index = np.where(~np.isnan(WVR_avg))[0][0]
# 
# Tsys_ext = Tsys_sci[0] * WVR_avg / WVR_avg[sci_ind0]


#############################
# plot Tsys vs WVR

fig = plt.figure()
plt.title('Tsys'+keywords_title)

# create color dictionary for the scatter plot
color_dict = { 'phase':'green', 'science':'blue', 'bandpass':'orange'}
legendhandle = [plt.plot([], marker=".", ls="", color=color)[0] for color in list(color_dict.values())]

# plot the scatter plot
plt.scatter(WVR_time, Tsys_ext, c=map_series_by_dict(obsTypes_WVR, color_dict))
plt.scatter(time_Tsys[:,0], Tsys_sinspw, s=dur_Tsys, color='red',linewidth=5,marker='_')

# label 
plt.xlabel('time (s)')
plt.ylabel('Tsys (K)')

# add legend
plt.legend(legendhandle,list(color_dict.keys()), loc='upper left', framealpha=0.5)

plt.savefig('Tsys_WVR'+keywords_filename+'.pdf')

#############################
# plot Tsky vs WVR

fig = plt.figure()
plt.title('Tsky'+keywords_title)

# create color dictionary for the scatter plot
color_dict = { 'phase':'green', 'science':'blue', 'bandpass':'orange'}
legendhandle = [plt.plot([], marker=".", ls="", color=color)[0] for color in list(color_dict.values())]

# plot the scatter plot
plt.scatter(WVR_time, Tsky_ext, c=map_series_by_dict(obsTypes_WVR, color_dict))
plt.scatter(time_Tsys[:,0], Tsky_sinspw, s=dur_Tsys, color='red',linewidth=5,marker='_')

# label 
plt.xlabel('time (s)')
plt.ylabel('Tsky (K)')

# add legend
plt.legend(legendhandle,list(color_dict.keys()), loc='upper left', framealpha=0.5)

plt.savefig('Tsky_WVR'+keywords_filename+'.pdf')


