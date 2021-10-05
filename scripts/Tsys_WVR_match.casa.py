import time
import pickle
import numpy as np

###########################################################
# basic settings

vis = 'uid___A002_Xec4ed2_X912.ms'

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


time_avg = 10
if time_avg == -1:
    timeAvg_txt = 'avg'
else:
    timeAvg_txt = str(time_avg) 

#############################
# Tsys table infomation

# column names of Tsys table dictionary
columns = ['info','iant','scan','obs_type','time_Tsys','dur_Tsys',
            'Tsys','Tsky','Trx','WVR_means','tau']
Tsys_table = dict.fromkeys(columns)

# info columns
info_columns = ['WVR chan','Tsys spw','avg time']
Tsys_table['info'] = dict.fromkeys(info_columns)
Tsys_table['vis'] = vis
Tsys_table['info']['WVR chan'] = np.array([0,1,2,3])
Tsys_table['info']['Tsys spw'] = np.array([17,19,21,23])
Tsys_table['info']['avg time'] = time_avg

# other columns
for key in columns:
    if key != 'info':
        Tsys_table[key] = np.array([])

# filename of the output pickle file
filename_Tsys = 'Tsys_WVR_matched_avgTime'+timeAvg_txt+'.pkl' 

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

def normalize_Tsys(Tsys_sinspw, isin_phase, isin_sci, isin_bpass):
    '''
    Normalize Tsys by the start of Tsys for phasecal, science and bandpass 
    respectively
    ---
    Parameters
    Tsys_sinspw: np.ndarray
        Tsys for single spectral window
    isin_phase: np.ndarray
        Indexes of Tsys for phasecal
    isin_sci: np.ndarray
        Indexes of Tsys for science observation
    isin_bpass: np.ndarray
        Indexes of Tsys for bandpass
    ------
    Return
    Tsys_norm: np.ndarray
        Normalized Tsys
    '''
    Tsys_norm = np.full(np.shape(Tsys_sinspw), np.nan)
    isins = [isin_phase, isin_sci, isin_bpass]

    for isin in isins:
        if len(isin[0]) == 0:
            continue
        else:
            Tsys_norm[isin] = Tsys_sinspw[isin] / Tsys_sinspw[isin[0][0]]

    return Tsys_norm

def select_spw_Tsys(Tsys, spws, spwid):
    '''
    Select Tsys with given spectral window
    ------
    Parameters
    Tsys: np.ndarray
        Averaged Tsys
    spws: np.ndarray
        Array of spectral window ids attached to each measurement
    spwid: int
        Spectral window to be selected
    ------
    Return
    Tsys_sinspw: np.ndarray
        Tsys with single spectral window
    '''

    Tsys_sinspw = Tsys[np.where(spws==spwid)]

    return Tsys_sinspw

###########################################################
# main program
start = time.time()

### read the WVR data 
tb.open(vis)
spw_WVR = 4
ddid = spw_WVR
scan_exclude = list(scan_checksource)
dat = tb.query('ANTENNA1==ANTENNA2 && DATA_DESC_ID==%d && SCAN_NUMBER not in %s'%(ddid,scan_exclude))
WVR = np.real(dat.getcol('DATA'))
WVR_time = dat.getcol('TIME').reshape(-1, nants)[:,0]
WVR_scans = dat.getcol('SCAN_NUMBER').reshape(-1, nants)[:,0]
dat.close()
tb.close()

WVR_temp = WVR[0].reshape(4, -1, nants)
WVR_temp = np.swapaxes(WVR_temp, 0, 1)

## exclude the hot and cold load in the WVR measurement
indices_load = np.unique(np.where(WVR_temp[:,3,:]>150)[0])
WVR_time[indices_load] = np.nan
WVR_temp[indices_load,:,:] = np.nan

## classify WVR data into different types of observation
elements = WVR_scans

test_elements = np.array(list(scan_phase)+list(np.intersect1d((scan_phase-1), scan_ATM)))
isin_phase_WVR = array_isin(elements, test_elements)

test_elements = np.array(list(scan_sci)+list(np.intersect1d((scan_sci-1), scan_ATM)))
isin_sci_WVR = array_isin(elements, test_elements)

test_elements = np.array(list(scan_bpass)+list(np.intersect1d((scan_bpass-1), scan_ATM)))
isin_bpass_WVR = array_isin(elements, test_elements)

isin_obsrs_WVR = [isin_phase_WVR, isin_sci_WVR, isin_bpass_WVR]

### read the optical depth
tb.open(vis+'/ASDM_CALATMOSPHERE')
tau_temp = tb.getcol('tau')
tau = np.mean(tau_temp, axis=0)
tau_mean = tau_temp.reshape(-1, 4)

### read the Tsys
tb.open(vis+'/SYSCAL')
tb3 = tb.query('')
iants = tb3.getcol('ANTENNA_ID').reshape(-1,4)[:,0]
Tsys_spectrum = tb3.getcol('TSYS_SPECTRUM')
Trx_spectrum = tb3.getcol('TRX_SPECTRUM')
Tsky_spectrum = tb3.getcol('TSKY_SPECTRUM')
Tsys_spws = tb3.getcol('SPECTRAL_WINDOW_ID')
tb3.close()
tb.close()

Tsys = average_Tsys(Tsys_spectrum).reshape(-1, 4)
Trx = average_Tsys(Trx_spectrum).reshape(-1, 4)
Tsky = average_Tsys(Tsky_spectrum).reshape(-1, 4)

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

## match the WVR data with Tsys measurements. 
WVR_means = np.full(np.shape(scan_ATM)+np.shape(WVR_temp)[1:], fill_value=np.nan)
isin_obsrs = [isin_phase, isin_sci, isin_bpass]
for i, isin_obs in enumerate(isin_obsrs):
    if len(isin_obs) !=0:
        WVR_time_obs = WVR_time[isin_obsrs_WVR[i]]
        WVR_obs = WVR_temp[isin_obsrs_WVR[i]]
        ind = find_nearest(WVR_time_obs, time_Tsys_avg[isin_obs])
        lowerTimes = WVR_time_obs[ind]
        upperTimes = WVR_time_obs[ind] + time_avg
        WVR_matched, indices_matched = filter_data(WVR_obs, WVR_time_obs, lowerTimes, upperTimes) 
        WVR_means[isin_obs] = np.stack([np.mean(data, axis=0) for data in WVR_matched], axis=0)

WVR_means = np.swapaxes(WVR_means,0,1)
WVR_means = WVR_means.reshape(4, -1)
    
Tsys_table['iant'] = iants 
Tsys_table['scan'] = np.repeat(scan_ATM, nants)
Tsys_table['obs_type'] = np.repeat(obs_type, nants)
Tsys_table['time_Tsys'] = np.repeat(time_Tsys_avg, nants)
Tsys_table['dur_Tsys'] = np.repeat(dur_Tsys, nants)
Tsys_table['Tsys'] = Tsys
Tsys_table['Tsky'] = Tsky
Tsys_table['Trx'] = Trx
Tsys_table['tau'] = tau_mean
Tsys_table['WVR_means'] = np.transpose(WVR_means)

with open(filename_Tsys, 'wb') as handle:
    pickle.dump(Tsys_table, handle)

stop = time.time()
count_time(stop, start)
