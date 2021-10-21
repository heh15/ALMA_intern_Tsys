import time
import pickle
import numpy as np
import matplotlib.pyplot as plt

###########################################################
# basic settings

vis = 'uid___A002_Xec4ed2_X912.ms'
matchpkl = 'Tsys_WVR_matched_avgTime10.pkl'
fitpkl = 'Tsys_WVR_fitted_WVRchan3_normScans000.pkl'

# number of antennas 
msmd.open(vis)
nants = msmd.nantennas()
msmd.done()
iants = np.arange(0, nants, 1)

# scan id 
msmd.open(vis)
scan_ATM = msmd.scansforintent('*CALIBRATE_ATMOSPHERE*')
scan_phase = msmd.scansforintent('*CALIBRATE_PHASE*')
scan_checksource = msmd.scansforintent('*OBSERVE_CHECK_SOURCE*')
scan_bpass = msmd.scansforintent('*CALIBRATE_BANDPASS*')
scan_sci = msmd.scansforintent('*OBSERVE_TARGET*')
msmd.done()

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
        shape = (len(spw_unique), len(Tsys)/len(spw_unique))
        Tsys_temp = np.full(shape, np.nan)
        for i, spw in enumerate(np.unique(spws)):
            Tsys_temp[i] = Tsys[np.where(spws==spw)]

        Tsys = np.mean(Tsys_temp, axis=0)

    return Tsys

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
        'science'). 
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


def extrapolate_data(ydata, xdata_norm, iants, obs_types, normScans=[0,0,0],
        fit_coeff=[1,0]):
    '''
    The function to extrapolate the data based on the normalized values
    from another array. 
    ------
    Parameters:
    ydata: np.1darray
        The original data taken for extrapolation and comparison. 
    xdata_norm: np.1darray
        The normalized data used to extrapolate the other data. 
    iants: np.1darray
        Array of antenna ids.
    obs_types: np.1darray
        Arrray of observation types ('bandpass', 'phase' and 'science').
    normScans: list, optional
        Specify which measurement (1st, 2nd, ...) for each 
        type of observation of each antenna to be normalized to.
    fit_coeff: list, optional
        Specify the coefficient of linear regression to extrapolate the 
        normalized ydata from the xdata_norm.
    ------
    Return:
    ydata_ext: np.1darray
        The extrapolated data.
    '''

    ydata_ext = np.full(np.shape(xdata), fill_value=np.nan)
    iants_uq = np.unique(iants)
    obsTypes_uq = np.unique(obs_types)
    for iant in iants_uq:
        for i, obs in enumerate(obsTypes_uq):
            conditions = ((iants == iant) & (obs_types==obs))
            indices = np.where(conditions)
            ydata_start = array[indices][normScans[i]]
            ydata_norm_sub = xdata_norm[indices]*fit_coeff[0] +\
                    fit_coeff[1]
            ydata_ext[indices] = ydata_start * ydata_norm_sub

    return ydata_ext

###########################################################
# main program
start = time.time()

### create the alternative Tsys tables

# read the information from the original Tsys table
vis_tsys_in = vis + '.tsys'
tb.open(vis_tsys_in)
dat = tb.query('')
iants_Tsys = dat.getcol('ANTENNA1')
time_Tsys = dat.getcol('TIME')
field_Tsys = dat.getcol('FIELD_ID')
spws_Tsys = dat.getcol('SPECTRAL_WINDOW_ID')
scans_Tsys = dat.getcol('SCAN_NUMBER')
flag_Tsys = dat.getcol('FLAG')
snr_Tsys = dat.getcol('SNR')
paramerr_Tsys = dat.getcol('PARAMERR')
dat.close()
tb.close()

# create an alternative Tsys table with no values at begining
vis_tsys_out = vis.replace('.ms', '_sub.ms.tsys')
rmtables(vis_tsys_out)
os.system('cp -r '+vis_tsys_in+' '+vis_tsys_out)

# remove the data
tb.open(vis_tsys_out, nomodify=False)
nrows = tb.nrows()
tb.removerows(np.array(range(nrows)))
tb.flush()
tb.close()

### read the matched WVR and Tsys
with open(matchpkl, 'rb') as pickle_file:
    Tsys_table = pickle.load(pickle_file)
Tsys_spws = Tsys_table['info']['Tsys spw']
iants = Tsys_table['iant']
obs_types = Tsys_table['obs_type']
obs_types = obs_types.astype(str)
obsTypes_uq = np.unique(obs_types)

### read the information for the fitting
with open(fitpkl, 'rb') as pickle_file:
    fit_results = pickle.load(pickle_file)

WVR_chan = fit_results['info']['WVR chan']
normScans = fit_results['info']['norm scans']

WVR_data = Tsys_table['WVR_means'][:,WVR_chan]
WVR_norm = normalize_data(WVR_data, iants, obs_types, normScans=normScans)

### extrapolate the normalized Tsys
Tsys_norm_temp = np.full((4,)+np.shape(WVR_norm), np.nan)
for i, spw in enumerate(Tsys_spws):
    Tsys_norm_temp[i] = fit_results[spw]['coeff'][0] * WVR_norm +\
            fit_results[spw]['coeff'][1]
Tsys_norm_ext = Tsys_norm_temp.reshape(4, -1, nants)

## extrapolate Tsys spectrum
tb.open(vis_tsys_in)
dat = tb.query('')
Tsys_spec_in = dat.getcol('FPARAM')
Tsys_spec_orig = Tsys_spec_in.reshape(np.shape(Tsys_spec_in)[0:2]+(4,-1,nants))
dat.close()
tb.close()

Tsys_spec_ext = np.full(np.shape(Tsys_spec_orig), np.nan)

for i, obs in enumerate(obsTypes_uq):
    obsTypes_sinant = obs_types[np.where(iants==0)]
    isin_idx = np.where(obsTypes_sinant==obs)
    Tsys_spec_ext[:,:,:,isin_idx[0],:] = np.einsum('ijkm,klm->ijklm',
            Tsys_spec_orig[:,:,:,isin_idx[normScans[i]][0],:],
            Tsys_norm_ext[:,isin_idx[0],:])
    Tsys_spec_out = Tsys_spec_ext.reshape(np.shape(Tsys_spec_ext)[0:2]+(-1,))

# output the data into the new Tsys table 
tb.open(vis_tsys_out, nomodify=False)
tb.addrows(len(time_Tsys))
tb.putcol('TIME',time_Tsys) 
tb.putcol('FIELD_ID',field_Tsys) 
tb.putcol('SPECTRAL_WINDOW_ID',spws_Tsys) 
tb.putcol('ANTENNA1', iants_Tsys)
tb.putcol('ANTENNA2', np.full(np.shape(time_Tsys), -1))
tb.putcol('INTERVAL', np.full(np.shape(time_Tsys), 0)) 
tb.putcol('SCAN_NUMBER', scans_Tsys)
tb.putcol('OBSERVATION_ID', np.full(np.shape(time_Tsys), 0)) 
tb.putcol('FPARAM', Tsys_spec_out) 
tb.putcol('PARAMERR', paramerr_Tsys) 
tb.putcol('FLAG', flag_Tsys) 
tb.putcol('SNR', snr_Tsys)
tb.flush()
tb.close()

# # check if the extrapolated Tsys agrees with the original Tsys
# Tsys_in_avg = np.mean(Tsys_spec_in, axis=(0,1))
# Tsys_out_avg = np.mean(Tsys_spec_out, axis=(0,1))
# 
# fig = plt.figure()
# plt.scatter(Tsys_in_avg, Tsys_out_avg)

stop = time.time()
count_time(stop, start)
