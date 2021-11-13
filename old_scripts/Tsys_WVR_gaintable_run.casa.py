import time
import matplotlib.pyplot as plt
import numpy as np
import pickle

###########################################################
# basic settings

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

# WVR channel
chan_WVR  = 0 # WVR channels
if chan_WVR == -1:
    chanWVR_txt = 'avg'
else:
    chanWVR_txt = str(chan_WVR)

# Tsys spectral windows
spw_Tsys = -1 # Tsys spectral window
if spw_Tsys == -1:
    spwTsys_txt = 'avg'
    average_spw = True
else:
    spwTsys_txt = str(spw_Tsys)
    average_spw = False

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

scinormScan = 0
phasenormScan = 0
bpassnormScan = 0

time_avg = 10
if time_avg == -1:
    timeAvg_txt = 'avg'
else:
    timeAvg_txt = str(time_avg)

#############################
# WVR gain table information

# column names of Tsys table dictionary
columns = ['info','iant','scan','obs_type','WVR_time','WVR_sinchan',
            'WVR_norms', 'Tsys_exts','Tsys_starts','Tsys_origs']
WVR_table = dict.fromkeys(columns)

# info columns
info_columns = ['WVR chan','Tsys spw','avg time']
WVR_table['info'] = dict.fromkeys(info_columns)
WVR_table['info']['WVR chan'] = chan_WVR
WVR_table['info']['Tsys spw'] = spw_Tsys
WVR_table['info']['avg time'] = time_avg

# other columns
for key in columns:
    if key != 'info':
        WVR_table[key] = np.array([])

# filename of the output pickle file
filename_WVR = 'WVR_gaintable_chanWVR'+chanWVR_txt+'_spwTsys'+spwTsys_txt+'_avgTime'+timeAvg_txt+'.pkl'

###########################################################
# functions
def array_isin(element, test_elements):
    '''
    Test if element in one array is in another array
    ------
    Parameters
    element: np.ndarray
        Input array
    test_elements: np.ndarray
        The values against which to test each value of element. This 
        argument is flattened if it is an array or array_like. 
    ------
    Return
    isin: np.ndarray
        Indexes of element that in test_elements. 
    '''
    dist = np.abs(element[:, np.newaxis] - test_elements)
    diff = np.nanmin(dist, axis=1)
    isin = np.where(diff == 0)

    return isin

def average_Tsys(Tsys_spectrum, chan_trim=5, average_spw=False, spws=[]):
    '''
    Average the system temperature over the frequency axis
    ------
    Parameters
    Tsys_spectrum: np.ndarray
        The extracted Tsys spectrum from tb.getcol()
    chan_trim: int
        number of channels trimed at the edge of spectrum
    average_spw: bool
        This determines whether to average Tsys measurements over different 
    spectral windows. 
    spws: np.ndarray
        The extracted spectral window array for Tsys measurements
    ------
    Return 
    Tsys: np.ndarray
        Averaged Tsys
    '''
    Tsys_avg1 = np.mean(Tsys_spectrum, axis=0)
    Tsys_avg2 = Tsys_avg1[chan_trim: (len(Tsys_avg1)-chan_trim)]
    Tsys = np.mean(Tsys_avg2, axis=0)

    if (average_spw == True) and len(spws) != 0:
        spw_unique = np.unique(spws)
        shape = (int(len(spw_unique)), int(len(Tsys)/len(spw_unique)))
        Tsys_temp = np.full(shape, np.nan)
        for i, spw in enumerate(np.unique(spws)):
            Tsys_temp[i] = Tsys[np.where(spws==spw)]

        Tsys = np.mean(Tsys_temp, axis=0)

    return Tsys

def find_nearest(array, values, full=False):
    '''
    Find the index of the values in the array closest to the given value
    ------
    Parameters:
    array: numpy.ndarray
        numpy array to be matched
    values: numpy.ndarray or float
        values to be matched with numpy array
    full: bool, optional
        Switch determining the nature of return values. When it is False
        (default) just the index returned. When True, the difference 
        between matched array and given values are also returned
    ------
    Return:
    idx: int or int numpy array
        index of the closest value in array.
    diff: float or float numpy array
        Present only if `full`=True. Absolute difference between the 
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


def filter_data(data, time, lowerTimes, upperTimes):
    '''
    Filter out data within a list of certain time ranges
    ------
    parameters:
    data: np.1darray
        array of data to be filtered
    time: np.1darray
        time series of the data taken
    lowerTimes: np.1darray
        array of lower limit of time ranges
    upperTimes: np.ndarray
        arrray of upper limit of time ranges
    ------
    return:
    data_matched: np.1darray
        Data that was filtered out
    idxSecs: np.1darray
        List of indices for different time ranges
    '''
    idxSecs = []
    for i, lowerTime in enumerate(lowerTimes):
        conditions = ((time >= lowerTimes[i]) & (time <= (upperTimes[i])))
        idxSec = np.where(conditions)
        idxSecs.append(idxSec[0])
    idxSecs = np.array(idxSecs)

    data_matched = []
    for idxSec in idxSecs:
        data_temp = data[idxSec]
        data_matched.append(data_temp)

    return data_matched, idxSecs

def count_time(stop, start):
    '''
    Convert the time difference into human readable form. 
    '''
    dure=stop-start
    m,s=divmod(dure,60)
    h,m=divmod(m,60)
    print("%d:%02d:%02d" %(h, m, s))

    return

def rebin_time(data, time, timebin=10, method='mean'):
    
    time_sep = np.arange(time[0], time[-1], timebin) + timebin/2
    data_binned = np.full(np.shape(time_sep), np.nan)

    # following code are similar as that in regrid_time()
    dist = np.abs(time[:, np.newaxis] - time_sep)
    potentialClosest = dist.argmin(axis=1)
    diff = dist.min(axis=1)
    # leave out the time with spacing greater than the interval of original time.
    data[np.where(diff > timebin)] = np.nan         
    closestFound, closestCounts = np.unique(potentialClosest, return_counts=True)
    data_group = np.split(data, np.cumsum(closestCounts)[:-1])
    if method == 'mean':
        for i, index in enumerate(closestFound):
            data_binned[index] = np.nanmean(data_group[i])
    if method == 'counts':
        for i, index in enumerate(closestFound):
            value, counts = np.unique(data_group[i], return_counts=True)
            ind = np.nanargmax(counts)
            data_binned[index] = value[ind]   

    return data_binned, time_sep


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
        data_binned = np.full(np.shape(time_binned), np.nan)

        # match the WVR in the each group with the new regrided time
        dist = np.abs(time_groups[i][:, np.newaxis] - time_binned)
        potentialclosest = dist.argmin(axis=1)
        diff = dist.min(axis=1)
        # leave out the time with spacing greater than the interval of original time.
        data[np.where(diff > timebin)] = np.nan
        closestfound, closestcounts = np.unique(potentialclosest, return_counts=True)
        data_group = np.split(data, np.cumsum(closestcounts)[:-1])
        for j, index in enumerate(closestfound):
            data_binned[index] = np.nanmean(data_group[j])
        WVR_groups_new.append(data_binned)
        time_groups_new.append(time_binned)

    WVR_out = np.concatenate(WVR_groups_new)
    time_out = np.concatenate(time_groups_new)

    return WVR_out, time_out


###########################################################
# main program
start = time.time()

iants = np.array([10])

for iant in iants:
    ### read the WVR data 
    tb.open(vis)
    spw_WVR = 4
    ddid = spw_WVR
    scan_exclude = list(scan_checksource)
    dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID==%d && SCAN_NUMBER not in %s'%(iant,iant,ddid,scan_exclude))
    WVR = np.real(dat.getcol('DATA'))
    WVR_avg = np.mean(WVR, axis=(0,1))
    WVR_time = dat.getcol('TIME')
    WVR_scans = dat.getcol('SCAN_NUMBER')
    WVR_field = dat.getcol('FIELD_ID')
    WVR_flag = dat.getcol('FLAG')
    tb.close()

    ## exclude the hot and cold load in the WVR measurement
    WVR_time[np.where(WVR[0][3]>150)] = np.nan
    WVR[:,:,np.where(WVR[0][3]>150)] = np.nan

    ## average the 4 different WVR channels with the weighting
    if chan_WVR == -1:
        weights = WVR[0]/275 * (WVR[0]/275-1)
        WVR_sinchan = np.average(WVR[0], axis=0, weights=weights)
    else:
        WVR_sinchan = WVR[0][chan_WVR]

    ## rebin the WVR for every 10 seconds.

    WVR_sinchan_binned, WVR_time_binned = rebin_WVR(WVR_sinchan, WVR_time, WVR_scans, timebin=10)
    WVR_scans_temp = WVR_scans.astype(float) 
    WVR_scans_binned  = rebin_WVR(WVR_scans_temp,WVR_time,WVR_scans, timebin=10)[0]
    WVR_scans_binned[np.isnan(WVR_scans_binned)] = -1
    WVR_scans_binned = WVR_scans_binned.astype(int)

    WVR_field_temp = WVR_field.astype(float)
    WVR_field_binned  = rebin_WVR(WVR_field_temp,WVR_time,WVR_scans,timebin=10)[0]
    WVR_field_binned[np.isnan(WVR_field_binned)] = -1
    WVR_field_binned = WVR_field_binned.astype(int)

    ## remove the nan values in the rebinned data
    WVR_time_binned = WVR_time_binned[~np.isnan(WVR_sinchan_binned)]
    WVR_scans_binned = WVR_scans_binned[~np.isnan(WVR_sinchan_binned)]
    WVR_field_binned = WVR_field_binned[~np.isnan(WVR_sinchan_binned)]
    WVR_sinchan_binned = WVR_sinchan_binned[~np.isnan(WVR_sinchan_binned)]
     
    ## classify WVR data into different types of observation
    obs_types_WVR = np.full(np.shape(WVR_sinchan_binned), fill_value=' ', dtype="S10")
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

    isin_obsrs_WVR = [isin_phase_WVR, isin_sci_WVR, isin_bpass_WVR]

    ### read the Tsys
    tb.open(vis+'/SYSCAL')
    tb3 = tb.query('ANTENNA_ID==%d'%(iant))
    Tsys_spectrum = tb3.getcol('TSYS_SPECTRUM')
    Trx_spectrum = tb3.getcol('TRX_SPECTRUM')
    Tsky_spectrum = tb3.getcol('TSKY_SPECTRUM')
    spws = tb3.getcol('SPECTRAL_WINDOW_ID')
    time_Tsys_temp = tb3.getcol('TIME')
    interval_Tsys = tb3.getcol('INTERVAL')
    tb.close()

    Tsys = average_Tsys(Tsys_spectrum, average_spw=True, spws=spws)
    Trx = average_Tsys(Trx_spectrum, average_spw=True, spws=spws)
    Tsky = average_Tsys(Tsky_spectrum, average_spw=True, spws=spws)

    ## select Tsys from a single spectral window
    if average_spw == False:
        Tsys_sinspw = select_spw_Tsys(Tsys, spws, np.unique(spws)[0])
        Trx_sinspw = select_spw_Tsys(Trx, spws, np.unique(spws)[0])
        Tsky_sinspw = select_spw_Tsys(Tsky, spws, np.unique(spws)[0])
    else:
        Tsys_sinspw = Tsys
        Trx_sinspw = Trx
        Tsky_sinspw = Tsky

    ## time for the system temperature
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

    ## match the system temperature with different observed data types 
    elements = scan_ATM + 1

    test_elements = scan_sci
    isin_sci = array_isin(elements, test_elements)

    test_elements = scan_phase
    isin_phase = array_isin(elements, test_elements)

    test_elements = scan_bpass
    isin_bpass = array_isin(elements, test_elements)

    isin_obsrs = [isin_phase, isin_sci, isin_bpass]

    ### normalize the WVR and extrapolate Tsys based on the start of Tsys

    normScans = [phasenormScan, scinormScan, bpassnormScan]
    WVR_norm_binned = np.full(np.shape(WVR_sinchan_binned), np.nan)
    Tsys_exts = np.full(np.shape(WVR_sinchan_binned), np.nan)
    Tsys_starts = np.full(np.shape(WVR_sinchan_binned), np.nan)
    Tsys_origs = np.full(np.shape(WVR_sinchan_binned), np.nan)

    for i, isin_obs in enumerate(isin_obsrs):
        if len(isin_obs) ==0:
            continue
        Tsys_start = Tsys_sinspw[isin_obs][normScans[i]]
        time_Tsys_start = time_Tsys_avg[isin_obs][normScans[i]]
        ind0 = find_nearest(WVR_time_binned, time_Tsys_start)
        WVR_obs = WVR_sinchan_binned[isin_obsrs_WVR[i]] 
        WVR_norm_binned[isin_obsrs_WVR[i]] = WVR_obs / WVR_sinchan_binned[ind0]
        Tsys_exts[isin_obsrs_WVR[i]] = Tsys_start *\
                                    WVR_norm_binned[isin_obsrs_WVR[i]] 
        Tsys_starts[isin_obsrs_WVR[i]] = Tsys_start
        scan_type = scan_ATM[isin_obs] + 1
    
        # match the original Tsys with the extrapolated Tsys.     
        inds_reverse, diff = find_nearest(scan_type, WVR_scans_binned, full=True)
        inds_matched = np.where(diff==0)
        if len(inds_matched) > 0:
            Tsys_origs[inds_matched] = Tsys_sinspw[isin_obs][inds_reverse[inds_matched]] 
        # for ATM cal
        inds_reverse, diff = find_nearest(scan_ATM[isin_obs], WVR_scans_binned, full=True) 
        inds_matched = np.where(diff==0)
        if len(inds_matched) > 0:
            Tsys_origs[inds_matched] = Tsys_sinspw[isin_obs][inds_reverse[inds_matched]]


    ### write the WVR table into the dictionary.

    iant_column = np.full(np.shape(WVR_sinchan_binned), fill_value=iant)
    WVR_table['iant'] = np.append(WVR_table['iant'], iant_column)
    WVR_table['scan'] = np.append(WVR_table['scan'], WVR_scans_binned)
    WVR_table['obs_type'] = np.append(WVR_table['obs_type'], obs_types_WVR)
    WVR_table['WVR_time'] = np.append(WVR_table['WVR_time'], WVR_time_binned)
    WVR_table['WVR_sinchan'] = np.append(WVR_table['WVR_sinchan'], WVR_sinchan_binned)
    WVR_table['WVR_norms'] = np.append(WVR_table['WVR_norms'], WVR_norm_binned)
    WVR_table['Tsys_exts'] = np.append(WVR_table['Tsys_exts'], Tsys_exts)
    WVR_table['Tsys_starts'] = np.append(WVR_table['Tsys_starts'], Tsys_starts)
    WVR_table['Tsys_origs'] = np.append(WVR_table['Tsys_origs'], Tsys_origs)

with open(filename_WVR, 'wb') as handle:
    pickle.dump(WVR_table, handle)

stop = time.time()
count_time(stop, start)

# # test 1
# Tsys_temp = np.mean(Tsys_spec_ext, axis=0)
# Tsys_temp = Tsys_temp[5:(len(Tsys_temp)-5)]
# Tsys_test = np.nanmean(Tsys_temp, axis=0)
# fig = plt.figure()
# # plt.scatter(WVR_time, Tsys_ext2)
# plt.scatter(time_Tsys3, Tsys_test, color='red')
# plt.ylim(bottom=100)
# 
# # test 2
# fig = plt.figure()
# plt.scatter(WVR_time, WVR_sinchan)
# plt.scatter(WVR_time_binned, WVR_sinchan_binned, color='red')
# 
# # test the gcal table time
# tb.open('uid___A002_Xe48598_X7857_v3_tsys_WVR.gcal', nomodify=False)
# test_time = tb.getcol('TIME')
# test_data = np.real(tb.getcol('CPARAM'))[0][0]
# tb.close()
# fig = plt.figure()
# plt.scatter(test_time, test_data)

# # test 3
# fig = plt.figure()
# plt.scatter(WVR_time, WVR_scans)
# plt.scatter(WVR_time_binned, WVR_scans_binned)
# 
# # test 4
# fig = plt.figure()
# plt.scatter(WVR_time, WVR_scans)
# plt.scatter(WVR_time_binned, WVR_scans_binned)

