import time
import matplotlib.pyplot as plt
import numpy as np
import pickle

###########################################################
# basic settings

vis = 'uid___A002_Xec4ed2_X912.ms'
filename_match = 'Tsys_WVR_matched_avgTime10.pkl'
filename_fit = 'Tsys_WVR_fitted_WVRchan3_normScans000.pkl' 

## information from the measurement set 
# number of antennas 
msmd.open(vis)
nants = msmd.nantennas()
msmd.done()
iants = np.arange(0, nants, 1)
# iants = np.delete(iants, np.argwhere(iants == 30)) # antenna 30 has weird Tsys values

# scan id 
msmd.open(vis)
scan_ATM = msmd.scansforintent('*CALIBRATE_ATMOSPHERE*')
scan_phase = msmd.scansforintent('*CALIBRATE_PHASE*')
scan_checksource = msmd.scansforintent('*OBSERVE_CHECK_SOURCE*')
scan_bpass = msmd.scansforintent('*CALIBRATE_BANDPASS*')
scan_sci = msmd.scansforintent('*OBSERVE_TARGET*')
msmd.done()

## informatoin from the 'filename_match'.
with open(filename_match, 'rb') as pickle_file:
    Tsys_table = pickle.load(pickle_file)
timebin = Tsys_table['info']['avg time']
Tsys_spws = Tsys_table['info']['Tsys spw']

obs_types = Tsys_table['obs_type'].reshape(-1,nants)[:,0]
time_Tsys = Tsys_table['time_Tsys'].reshape(-1,nants)[:,0]
Tsys = Tsys_table['Tsys']

## information from the 'fiename_fit'
with open(filename_fit, 'rb') as pickle_file:
    fit_results = pickle.load(pickle_file)
chan_WVR = fit_results['info']['WVR chan']
normScans = fit_results['info']['norm scans']

#############################
# WVR gain table information

# column names of Tsys table dictionary
WVR_table = {}

# info columns
WVR_table['info'] = {}
info_columns = ['WVR chan','Tsys spw','avg time']
WVR_table['info'] = dict.fromkeys(info_columns)
WVR_table['info']['WVR chan'] = chan_WVR
WVR_table['info']['Tsys spw'] = Tsys_spws
WVR_table['info']['avg time'] = timebin
WVR_table['info']['norm scans'] = normScans

# filename of the output pickle file
filename_WVR = 'WVR_gaintable_chanWVR'+str(chan_WVR)+'_avgtime'+str(timebin)+'.pkl'

###########################################################
# functions
def array_isin(element, test_elements):
    '''
    test if element in one array is in another array
    ------
    parameters
    element: np.ndarray
        input array
    test_elements: np.ndarray
        the values against which to test each value of element. this 
        argument is flattened if it is an array or array_like. 
    ------
    return
    isin: np.ndarray
        indexes of element that in test_elements. 
    '''
    dist = np.abs(element[:, np.newaxis] - test_elements)
    diff = np.nanmin(dist, axis=1)
    isin = np.where(diff == 0)

    return isin

def find_nearest(array, values, full=False):
    '''
    find the index of the values in the array closest to the given value
    ------
    parameters:
    array: numpy.ndarray
        numpy array to be matched
    values: numpy.ndarray or float
        values to be matched with numpy array
    full: bool, optional
        switch determining the nature of return values. when it is false
        (default) just the index returned. when true, the difference 
        between matched array and given values are also returned
    ------
    return:
    idx: int or int numpy array
        index of the closest value in array.
    diff: float or float numpy array
        present only if `full`=true. absolute difference between the 
        given values and matched values in the array. 
    '''
    array = np.asarray(array)
    dist = np.abs(array[:,np.newaxis] - values)
    idx = np.nanargmin(dist, axis=0)
    diff = np.nanmin(dist, axis=0)

    if full:
        return idx, diff
    else:
        return idx


def filter_data(data, time, lowertimes, uppertimes):
    '''
    filter out data within a list of certain time ranges
    ------
    parameters:
    data: np.1darray
        array of data to be filtered
    time: np.1darray
        time series of the data taken
    lowertimes: np.1darray
        array of lower limit of time ranges
    uppertimes: np.ndarray
        arrray of upper limit of time ranges
    ------
    return:
    data_matched: np.1darray
        data that was filtered out
    idxsecs: np.1darray
        list of indices for different time ranges
    '''
    idxsecs = []
    for i, lowertime in enumerate(lowertimes):
        conditions = ((time >= lowertimes[i]) & (time <= (uppertimes[i])))
        idxsec = np.where(conditions)
        idxsecs.append(idxsec[0])
    idxsecs = np.array(idxsecs)

    data_matched = []
    for idxsec in idxsecs:
        data_temp = data[idxsec]
        data_matched.append(data_temp)

    return data_matched, idxsecs

def count_time(stop, start):
    '''
    convert the time difference into human readable form. 
    '''
    dure=stop-start
    m,s=divmod(dure,60)
    h,m=divmod(m,60)
    print("%d:%02d:%02d" %(h, m, s))

    return

def rebin_WVR(WVR, time, WVR_scans, timebin=10):

    isnan_idx = np.isnan(time)
    WVR = WVR[~isnan_idx] 
    time = time[~isnan_idx]

    WVR_groups = np.split(WVR, np.unique(WVR_scans, return_index=True)[1])
    time_groups = np.split(time, np.unique(WVR_scans, return_index=True)[1])
    WVR_groups_new = []
    time_groups_new = []

    for i, WVR_scan in enumerate(np.unique(WVR_scans)):
        
        if len(time_groups[i]) == 0:
            continue

        data = WVR_groups[i]
        start_time = time_groups[i][0]
        stop_time = time_groups[i][-1]
        time_binned = np.arange(start_time, stop_time, timebin) + timebin/2
        data_binned = np.full(np.shape(time_binned)[0:1]+np.shape(WVR)[1:],
                np.nan)

        # match the WVR in the each group with the new regrided time
        dist = np.abs(time_groups[i][:, np.newaxis] - time_binned)
        potentialclosest = dist.argmin(axis=1)
        diff = dist.min(axis=1)
        # leave out the time with spacing greater than the interval of original time.
        data[np.where(diff > timebin)] = np.nan
        closestfound, closestcounts = np.unique(potentialclosest, return_counts=True)
        data_group = np.split(data, np.cumsum(closestcounts)[:-1])
        for j, index in enumerate(closestfound):
            data_binned[index] = np.nanmean(data_group[j],axis=0)
        WVR_groups_new.append(data_binned)
        time_groups_new.append(time_binned)

    WVR_out = np.concatenate(WVR_groups_new)
    time_out = np.concatenate(time_groups_new)

    return WVR_out, time_out


def normalize_data(data, iants, obs_types, normScans=[0,0,0]):
    '''
    Normalize the data by the first measurement of each antenna
    and each type of target (bandpass, phase and science)
    ---
    Parameters:
    data: np.1darray
        The data to be normalized. 
    iants:np.1darray
        Array of the antennas corresponding to the data
    obs_type: np.1darray
        Arrray of observation types ('bandpass', 'phase' and 
        'science'. 
    normScans: list, optional
        Specify which measurement (1st, 2nd, ...) for each 
        type of observation of each antenna to be normalized to.
    ---
    Return:
    data_norm: np.1darray
        The normalized data. 
    '''

    data_norm = np.full(np.shape(data), fill_value=np.nan)
    iants_uq = np.unique(iants)
    obsTypes_uq = np.unique(obs_types)
    for iant in iants_uq:
        for i, obs in enumerate(obsTypes_uq):
            conditions = ((iants == iant) & (obs_types==obs))
            indices = np.where(conditions)
            data_sub = data[indices]
            data_norm[indices] = data_sub / data_sub[normScans[i]]

    return data_norm


###########################################################
# main program
start = time.time()

### read the WVR data 
## read the data
tb.open(vis)
spw_WVR = 4
ddid = spw_WVR
scan_exclude = list(scan_checksource)
dat = tb.query('ANTENNA1==ANTENNA2 && DATA_DESC_ID==%d && SCAN_NUMBER not in %s'%(ddid,scan_exclude))
WVR = np.real(dat.getcol('DATA'))
WVR_time = dat.getcol('TIME').reshape(-1, nants)[:,0]
WVR_scans = dat.getcol('SCAN_NUMBER').reshape(-1, nants)[:,0]
WVR_field = dat.getcol('FIELD_ID').reshape(-1, nants)[:,0]
WVR_flag = dat.getcol('FLAG').reshape(-1, nants)[:,0]
tb.close()

WVR_temp = WVR[0].reshape(4, -1, nants)
WVR_temp = np.swapaxes(WVR_temp, 0, 1)

## exclude the hot and cold load in the WVR measurement
indices_load = np.unique(np.where(WVR_temp[:,3,:]>150)[0])
WVR_time[indices_load] = np.nan
WVR_temp[indices_load,:,:] = np.nan

## select WVR from the single channel
WVR_sinchan = WVR_temp[:,chan_WVR,:]

## rebin the WVR for every 10 seconds.

WVR_sinchan_binned, WVR_time_binned = rebin_WVR(WVR_sinchan,WVR_time,WVR_scans,timebin=timebin)
WVR_scans_temp = WVR_scans.astype(float) 
WVR_scans_binned  = rebin_WVR(WVR_scans_temp,WVR_time,WVR_scans,timebin=timebin)[0]
WVR_scans_binned[np.isnan(WVR_scans_binned)] = -1
WVR_scans_binned = WVR_scans_binned.astype(int)

WVR_field_temp = WVR_field.astype(float)
WVR_field_binned  = rebin_WVR(WVR_field_temp,WVR_time,WVR_scans,timebin=timebin)[0]
WVR_field_binned[np.isnan(WVR_field_binned)] = -1
WVR_field_binned = WVR_field_binned.astype(int)

## remove the nan values in the rebinned data
indices_nan = np.unique(np.isnan(WVR_sinchan_binned)[0])
WVR_sinchan_binned[indices_nan,:] = np.nan 
WVR_time_binned = WVR_time_binned[~np.isnan(WVR_sinchan_binned[:,0])]
WVR_scans_binned = WVR_scans_binned[~np.isnan(WVR_sinchan_binned[:,0])]
WVR_field_binned = WVR_field_binned[~np.isnan(WVR_sinchan_binned[:,0])]
WVR_sinchan_binned = WVR_sinchan_binned[~np.isnan(WVR_sinchan_binned[:,0]),:]
     
## classify WVR data into different types of observation
obs_types_WVR = np.full(np.shape(WVR_time_binned), fill_value=' ', dtype="S10")
elements = WVR_scans_binned

test_elements = np.array(list(scan_phase)+list(np.intersect1d((scan_phase-1), scan_ATM)))
isin_phase_WVR = array_isin(elements, test_elements)
obs_types_WVR[isin_phase_WVR] = 'phase'

test_elements = np.array(list(scan_sci)+list(np.intersect1d((scan_sci-1), scan_ATM)))
isin_sci_WVR = array_isin(elements, test_elements)
obs_types_WVR[isin_sci_WVR] = 'science'

test_elements = np.array(list(scan_bpass)+list(np.intersect1d((scan_bpass-1), scan_ATM)))
isin_bpass_WVR = array_isin(elements, test_elements)
obs_types_WVR[isin_bpass_WVR] = 'bandpass'

### normalize the WVR and extrapolate Tsys based on the start of Tsys

# normalize the WVR data
WVR_norm_binned = np.full(np.shape(WVR_sinchan_binned), np.nan)
obsTypes_uq = np.unique(obs_types)
for i, obs in enumerate(obsTypes_uq):
    isin_obs = np.where(obs_types == obs)
    isin_obs_WVR = np.where(obs_types_WVR == obs)
    time_Tsys_start = time_Tsys[isin_obs][normScans[i]]
    ind0 = find_nearest(WVR_time_binned, time_Tsys_start)
    WVR_obs = WVR_sinchan_binned[isin_obs_WVR] 
    WVR_norm_binned[isin_obs_WVR] = WVR_obs / WVR_sinchan_binned[ind0]

# calculate the normalized Tsys from normalized WVR
Tsys_reshaped = Tsys.reshape(-1,nants,4)
Tsys_norm_ext = np.full(np.shape(WVR_norm_binned)+(4,), np.nan)
for i, spw in enumerate(Tsys_spws):
    Tsys_norm_ext[:,:,i] = fit_results[spw]['coeff'][0] * WVR_norm_binned +\
            fit_results[spw]['coeff'][1]

# calculate the extrapolated Tsys.
Tsys_ext = np.full(np.shape(WVR_norm_binned)+(4,), np.nan)
Tsys_start = np.full(np.shape(WVR_norm_binned)+(4,), np.nan)
Tsys_orig = np.full(np.shape(WVR_norm_binned)+(4,), np.nan)
for i, obs in enumerate(obsTypes_uq):
    isin_obs = np.where(obs_types == obs)[0]
    isin_obs_WVR = np.where(obs_types_WVR == obs)[0]
    Tsys_start_value = Tsys_reshaped[isin_obs][normScans[i]]
    Tsys_ext[isin_obs_WVR] = np.einsum('jk,ijk->ijk', Tsys_start_value, 
            Tsys_norm_ext[isin_obs_WVR])
    Tsys_start[isin_obs_WVR] = Tsys_start_value

    # match the original Tsys with the extrapolated Tsys
    scan_type = scan_ATM[isin_obs] + 1
    inds_reverse, diff = find_nearest(scan_type, WVR_scans_binned, full=True)
    inds_matched = np.where(diff==0)
    if len(inds_matched) > 0:
        Tsys_orig[inds_matched] = Tsys_reshaped[isin_obs][inds_reverse[inds_matched]]
    # match the ATM cal
    inds_reverse, diff = find_nearest(scan_ATM[isin_obs], WVR_scans_binned, full=True)
    inds_matched = np.where(diff==0)
    if len(inds_matched) > 0:
        Tsys_orig[inds_matched] = Tsys_reshaped[isin_obs][inds_reverse[inds_matched]]

# remove the nan values in WVR_norms_binned
nan_mask = np.isnan(WVR_norm_binned[:,0])
WVR_time_binned = WVR_time_binned[~nan_mask]
WVR_scans_binned = WVR_scans_binned[~nan_mask]
WVR_field_binned = WVR_field_binned[~nan_mask]
obs_types_WVR = obs_types_WVR[~nan_mask]
WVR_sinchan_binned = WVR_sinchan_binned[~nan_mask,:]
WVR_norm_binned = WVR_norm_binned[~nan_mask,:]
Tsys_norm_ext = Tsys_norm_ext[~nan_mask,:,:]
Tsys_ext = Tsys_ext[~nan_mask,:,:]
Tsys_start = Tsys_start[~nan_mask,:,:]
Tsys_orig = Tsys_orig[~nan_mask,:,:]

# remove the axis for different antennas. 
WVR_data_out = WVR_sinchan_binned.flatten()
WVR_norm_out = WVR_norm_binned.flatten()
Tsys_norm_out = Tsys_norm_ext.reshape(-1,4)
Tsys_ext_out = Tsys_ext.reshape(-1,4)
Tsys_start_out = Tsys_start.reshape(-1,4)
Tsys_orig_out = Tsys_orig.reshape(-1,4)

### write the WVR table into the dictionary.
WVR_table['iant'] = np.tile(np.arange(nants), len(WVR_time_binned))
WVR_table['scan'] = np.repeat(WVR_scans_binned, nants)
WVR_table['field'] = np.repeat(WVR_field_binned, nants)
WVR_table['obs_type'] = np.repeat(obs_types_WVR, nants)
WVR_table['WVR_time'] = np.repeat(WVR_time_binned, nants)
WVR_table['WVR_data'] = WVR_data_out
WVR_table['WVR_norm'] = WVR_norm_out
WVR_table['Tsys_norm'] = Tsys_norm_out
WVR_table['Tsys_ext'] = Tsys_ext_out
WVR_table['Tsys_start'] = Tsys_start_out
WVR_table['Tsys_orig'] = Tsys_orig_out

with open(filename_WVR, 'wb') as handle:
    pickle.dump(WVR_table, handle)

stop = time.time()
count_time(stop, start)

# test
iants = WVR_table['iant']
Tsys_sinant = Tsys_ext[:,10,0]
Tsys_orig_sinant = Tsys_orig[:,10,0]
time_sinant = WVR_table['WVR_time'][np.where(iants==10)]
fig = plt.figure()
plt.scatter(time_sinant, Tsys_sinant, color='blue')
plt.scatter(time_sinant, Tsys_orig_sinant, color='red')
plt.scatter(time_Tsys, Tsys_reshaped[:,10,0],color='red')

