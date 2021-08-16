import time
import pickle
import numpy as np

###########################################################
# basic settings

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

# WVR channel
chan_WVR  = -1 # WVR channels
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

# scan_ATM = np.array([2,5,8,10, 12, 16,18, 20, 24, 26, 28, 32, 34])
# scan_phase = np.array([6,11,14,19,22,27,30,35])
# scan_checksource = np.array([7, 15, 23, 31])
# scan_bpass = np.array([3])
# scan_sci = np.array([7,9,13,17,21,25,29,33])

scinormScan  = 0
phasenormScan = 0
bpassnormScan = 0

time_avg = 10
if time_avg == -1:
    timeAvg_txt = 'avg'
else:
    timeAvg_txt = str(time_avg) 

#############################
# Tsys table infomation

# column names of Tsys table dictionary
columns = ['info','iant','scan','obs_type','time_Tsys','dur_Tsys',
            'Tsys','Tsys_norm','Tsky','Tsky_norm','Trx','Trx_norm',
            'WVR_means','WVR_norms','tau_mean']
Tsys_table = dict.fromkeys(columns)

# info columns
info_columns = ['WVR chan','Tsys spw','avg time']
Tsys_table['info'] = dict.fromkeys(info_columns)
Tsys_table['info']['WVR chan'] = chan_WVR 
Tsys_table['info']['Tsys spw'] = spw_Tsys
Tsys_table['info']['avg time'] = time_avg

# other columns
for key in columns:
    if key != 'info':
        Tsys_table[key] = np.array([])

# filename of the output pickle file
filename_Tsys = 'Tsys_WVR_correlation_chanWVR'+chanWVR_txt+'_spwTsys'+spwTsys_txt+'_avgTime'+timeAvg_txt+'.pkl' 

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

for iant in iants:
    iant_column = np.full(np.shape(scan_ATM), fill_value=iant)

    # get the corresponding antenna names
    msmd.open(vis)
    antenna_name = msmd.antennanames(iant)[0]
    msmd.done()

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
    tb.close()

    ## exclude the hot and cold load in the WVR measurement
    WVR_time[np.where(WVR[0][0]>200)] = np.nan
    WVR[np.where(WVR > 200)] = np.nan

    ## average the 4 different WVR channels with the weighting
    if chan_WVR == -1:
        weights = WVR[0]/275 * (WVR[0]/275-1)
        WVR_sinchan = np.average(WVR[0], axis=0, weights=weights)
    else:
        WVR_sinchan = WVR[0][chan_WVR]

    ## classify WVR data into different types of observation
    elements = WVR_scans

    test_elements = np.array(list(scan_phase)+list(np.intersect1d((scan_phase-1), scan_ATM)))
    isin_phase_WVR = array_isin(elements, test_elements)
    WVR_phase = WVR_sinchan[isin_phase_WVR]; time_WVR_phase = WVR_time[isin_phase_WVR]

    test_elements = np.array(list(scan_sci)+list(np.intersect1d((scan_sci-1), scan_ATM)))
    isin_sci_WVR = array_isin(elements, test_elements)
    WVR_sci = WVR_sinchan[isin_sci_WVR]; time_WVR_sci = WVR_time[isin_sci_WVR]

    test_elements = np.array(list(scan_bpass)+list(np.intersect1d((scan_bpass-1), scan_ATM)))
    isin_bpass_WVR = array_isin(elements, test_elements)
    WVR_bpass = WVR_sinchan[isin_bpass_WVR]; time_WVR_bpass = WVR_time[isin_bpass_WVR]

    isin_obsrs_WVR = [isin_phase_WVR, isin_sci_WVR, isin_bpass_WVR]

    ### read the optical depth
    tb.open(vis+'/ASDM_CALATMOSPHERE')
    antennaName = tb.getcol('antennaName')
    tau = tb.getcol('tau')
    # select specific antenna, average over polarizations and spws
    tau_mean = np.mean(tau, axis=0)
    tau_mean = tau_mean[np.where(antennaName==antenna_name)]
    tau_mean = np.mean(tau_mean.reshape(-1, 4), axis=1) 
    tb.close()

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

    Tsys_norm = normalize_Tsys(Tsys_sinspw, isin_phase, isin_sci, isin_bpass)
    Tsky_norm = normalize_Tsys(Tsky_sinspw, isin_phase, isin_sci, isin_bpass)
    Trx_norm = normalize_Tsys(Trx_sinspw, isin_phase, isin_sci, isin_bpass)

    ### normalize the WVR data based on the start of Tsys

    normScans = [phasenormScan, scinormScan, bpassnormScan]
    WVR_means = np.full(np.shape(scan_ATM), fill_value=np.nan)
    WVR_norms = np.full(np.shape(scan_ATM), fill_value=np.nan)

    isin_obsrs = [isin_phase, isin_sci, isin_bpass]
    for i, isin_obs in enumerate(isin_obsrs):
        if len(isin_obs) !=0:
            WVR_time_obs = WVR_time[isin_obsrs_WVR[i]]
            WVR_obs = WVR_sinchan[isin_obsrs_WVR[i]]
            ind = find_nearest(WVR_time_obs, time_Tsys_avg[isin_obs])

            # match the WVR with Tsys within 10 seconds and then normalize WVR
            lowerTimes = WVR_time_obs[ind]
            upperTimes = WVR_time_obs[ind] + time_avg
            WVR_matched, indices_matched = filter_data(WVR_obs, WVR_time_obs, lowerTimes, upperTimes) 
            WVR_means[isin_obs] = np.array([np.mean(data) for data in WVR_matched])
            WVR_norms[isin_obs] = WVR_means[isin_obs] / WVR_means[isin_obs][normScans[i]]
              
    # write the Tsys table
    Tsys_table['iant'] = np.append(Tsys_table['iant'], iant_column)
    Tsys_table['scan'] = np.append(Tsys_table['scan'], scan_ATM)
    Tsys_table['obs_type'] = np.append(Tsys_table['obs_type'], obs_type)
    Tsys_table['time_Tsys'] = np.append(Tsys_table['time_Tsys'], time_Tsys_avg)
    Tsys_table['dur_Tsys'] = np.append(Tsys_table['dur_Tsys'], dur_Tsys) 
    Tsys_table['Tsys'] = np.append(Tsys_table['Tsys'], Tsys_sinspw)
    Tsys_table['Tsys_norm'] = np.append(Tsys_table['Tsys_norm'], Tsys_norm) 
    Tsys_table['Tsky'] = np.append(Tsys_table['Tsky'], Tsky_sinspw)
    Tsys_table['Tsky_norm'] = np.append(Tsys_table['Tsky_norm'], Tsky_norm) 
    Tsys_table['Trx'] = np.append(Tsys_table['Trx'], Trx_sinspw)
    Tsys_table['Trx_norm'] = np.append(Tsys_table['Trx_norm'], Trx_norm) 
    Tsys_table['WVR_means'] = np.append(Tsys_table['WVR_means'],WVR_means)
    Tsys_table['WVR_norms'] = np.append(Tsys_table['WVR_norms'],WVR_norms)
    Tsys_table['tau_mean'] = np.append(Tsys_table['tau_mean'], tau_mean)

    # write the WVR table and extrapolated Tsys and Tsky

with open(filename_Tsys, 'wb') as handle:
    pickle.dump(Tsys_table, handle)

stop = time.time()
count_time(stop, start)
