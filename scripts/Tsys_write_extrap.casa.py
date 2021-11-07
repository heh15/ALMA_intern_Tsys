import time
import pickle
import matplotlib.pyplot as plt
import numpy as np

###########################################################
# basic settings

vis = 'uid___A002_Xec4ed2_X912.ms'

filename_Tsys = 'Tsys_WVR_matched_avgTime10.pkl' 
filename_gain = 'WVR_gaintable_chanWVR3_avgtime10.pkl' 

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


###########################################################
# main program
start = time.time()

### create the alternative Tsys tables
vis_tsys_in = vis + '.tsys'
vis_tsys_out = vis.replace('.ms', '_extrap.ms.tsys')
rmtables(vis_tsys_out)
os.system('cp -r '+vis_tsys_in+' '+vis_tsys_out)

tb.open(vis_tsys_out, nomodify=False)
nrows = tb.nrows()
tb.removerows(np.array(range(nrows)))
tb.flush()
tb.close()

### create a new gain table
# copy the info from amplitude gain table
vis_amp_gain = vis+'.split.ampli_inf'
vis_tsys_gain = vis.replace('.ms', '_extrap_tsys_WVR.gcal') 
rmtables(vis_tsys_gain)
os.system('cp -r '+vis_amp_gain+' '+vis_tsys_gain)

tb.open(vis_tsys_gain, nomodify=False)
nrows = tb.nrows()
tb.removerows(np.array(range(nrows)))
tb.putkeyword("MSName", vis) 
tb.flush()
tb.close()

### read the information of the Tsys table
with open(filename_Tsys,'rb') as pickle_file:
    Tsys_table = pickle.load(pickle_file)
spws = np.array(Tsys_table['info']['Tsys spw'])
iants = Tsys_table['iant']
obs_types = Tsys_table['obs_type'][np.where(iants==0)]
obsTypes_uq = np.unique(obs_types)

### read the extrapolated normalized Tsys
with open(filename_gain, 'rb') as pickle_file:
    WVR_table = pickle.load(pickle_file)
WVR_time_binned = WVR_table['WVR_time']
gain_time = np.tile(WVR_table['WVR_time'],4)
gain_fields = np.tile(WVR_table['field'],4)
gain_iants = np.tile(WVR_table['iant'],4)
gain_scans = np.tile(WVR_table['scan'],4)
gain_data = np.transpose(WVR_table['Tsys_norm']).flatten()
gain_data = np.sqrt(1/gain_data)
gain_data = gain_data[np.newaxis,np.newaxis,:]

### write the normalized WVR data into gain table
tb.open(vis_tsys_gain, nomodify=False)
tb.addrows(len(gain_time))
tb.putcol('TIME', gain_time)
tb.putcol('FIELD_ID', gain_fields)
tb.putcol('SPECTRAL_WINDOW_ID', np.repeat(spws, len(WVR_time_binned)))
tb.putcol('ANTENNA1', gain_iants)
tb.putcol('ANTENNA2', np.full(np.shape(gain_time), -1))
tb.putcol('INTERVAL', np.full(np.shape(gain_time), 0))
tb.putcol('SCAN_NUMBER', gain_scans)
tb.putcol('OBSERVATION_ID', np.full(np.shape(gain_time),0))
tb.putcol('CPARAM', gain_data)
tb.putcol('PARAMERR', np.full(np.shape(gain_data), 0))
tb.putcol('FLAG', np.full(np.shape(gain_data), False))
tb.putcol('SNR', np.full(np.shape(gain_data), 1))
tb.flush()
tb.close()


### read the start of Tsys for each antenna and type of observation
normScans = WVR_table['info']['norm scans'] 

## read the Tsys information
tb.open(vis_tsys_in)
dat = tb.query('')
Tsys_specs = dat.getcol('FPARAM')
Tsys_time = dat.getcol('TIME')
Tsys_fields = dat.getcol('FIELD_ID')
Tsys_spws = dat.getcol('SPECTRAL_WINDOW_ID')
Tsys_iants = dat.getcol('ANTENNA1')
Tsys_scans = dat.getcol('SCAN_NUMBER')
Tsys_flags = dat.getcol('FLAG')
Tsys_paramerrs = dat.getcol('PARAMERR')
Tsys_snrs = dat.getcol('SNR')
tb.close()

## read the start Tsys into the new Tsys table. 
# get the index of Tsys to be extracted
idx1d = np.arange(0,len(Tsys_time),1)
idx1d_reshaped = idx1d.reshape(4,-1,nants)
idx1d_extrc = np.full((4,len(obsTypes_uq),nants),np.nan)
for i, obs in enumerate(obsTypes_uq):
    isin_obs = np.where(obs_types==obs)
    idx1d_extrc[:,i,:] = idx1d_reshaped[:,isin_obs[0][normScans[i]],:]
idx1d_out = idx1d_extrc.reshape(-1).astype('int')

# output the selected values into the new Tsys table
tb.open(vis_tsys_out, nomodify=False)
tb.addrows(len(idx1d_out))
tb.putcol('TIME', Tsys_time[idx1d_out])
tb.putcol('FIELD_ID', Tsys_fields[idx1d_out])
tb.putcol('SPECTRAL_WINDOW_ID',Tsys_spws[idx1d_out])
tb.putcol('ANTENNA1', Tsys_iants[idx1d_out])
tb.putcol('ANTENNA2', np.full(np.shape(idx1d_out), -1))
tb.putcol('INTERVAL', np.full(np.shape(idx1d_out), 0))
tb.putcol('SCAN_NUMBER', Tsys_scans[idx1d_out])
tb.putcol('OBSERVATION_ID', np.full(np.shape(idx1d_out), 0))
tb.putcol('FPARAM', Tsys_specs[:,:,idx1d_out])
tb.putcol('PARAMERR', Tsys_paramerrs[:,:,idx1d_out])
tb.putcol('FLAG', Tsys_flags[:,:,idx1d_out])
tb.putcol('SNR', Tsys_snrs[:,:,idx1d_out])
tb.flush()
tb.close()

# # test1, gaintable
# fig = plt.figure()
# gain_time_sinant = gain_time[np.where(gain_iants==0)]
# gain_data_sinant = gain_data[0][0][np.where(gain_iants==0)]
# plt.scatter(gain_time_sinant, gain_data_sinant)
# 
# # test2, Tsys table
# fig = plt.figure()
# Tsys_out_avg = np.mean(Tsys_specs[:,:,idx1d_out], axis=(0,1))
# Tsys_iants_out = Tsys_iants[idx1d_out]
# Tsys_time_out = Tsys_time[idx1d_out]
# Tsys_sinant = Tsys_out_avg[np.where(Tsys_iants_out==0)]
# Tsys_time_sinant = Tsys_time_out[np.where(Tsys_iants_out==0)]
# 
# gain_time_sinant = gain_time[np.where(gain_iants==0)]
# Tsys_ext_sinant = np.transpose(WVR_table['Tsys_ext']).flatten()[np.where(gain_iants==0)]
# 
# plt.scatter(gain_time_sinant, Tsys_ext_sinant, color='blue')
# plt.scatter(Tsys_time_sinant, Tsys_sinant, color='red')


stop = time.time()
count_time(stop, start)


