import time
import matplotlib.pyplot as plt

###########################################################
# basic settings

vis = 'uid___A002_Xbf792a_X14cc.ms'

chan_WVR = 1 # WVR channels
spw_Tsys = 17 # Tsys spectral window
average_spw = True

scinormScan = 0
phasenormScan = 0
bpassnormScan = 0

time_avg = 10

# get the number of antennaes
msmd.open(vis)
nants = msmd.nantennas()
msmd.done()
iants = range(nants)
# iants = range(1)

# get the scan number for different observations
msmd.open(vis)
scan_ATM = msmd.scansforintent('*CALIBRATE_ATMOSPHERE*')
scan_phase = msmd.scansforintent('*CALIBRATE_PHASE*')
scan_checksource = msmd.scansforintent('*OBSERVE_CHECK_SOURCE*')
scan_bpass = msmd.scansforintent('*CALIBRATE_BANDPASS*')
scan_sci = msmd.scansforintent('*OBSERVE_TARGET*')
msmd.done()

# scan_ATM = np.array([2, 5, 8, 10, 15, 17, 22, 24, 29, 31])
# scan_phase = np.array([6, 11, 13, 18, 20, 25, 27, 32, 34])
# scan_checksource = np.array([7, 14, 21, 28])
# scan_bpass = np.array([3])
# scan_sci = np.array([9, 12, 16, 19, 23, 26, 30, 33])

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
vis_tsys_out = vis.replace('.ms', '_v3.ms.tsys')
rmtables(vis_tsys_out)
os.system('cp -r '+vis_tsys_in+' '+vis_tsys_out)

tb.open(vis_tsys_out, nomodify=False)
nrows = tb.nrows()
tb.removerows(range(nrows))
tb.flush()
tb.close()

### create a new gain table
# copy the info from amplitude gain table
vis_amp_gain = vis+'.split.ampli_inf'
vis_tsys_gain = vis.replace('.ms', '_v3_tsys_WVR.gcal') 
rmtables(vis_tsys_gain)
os.system('cp -r '+vis_amp_gain+' '+vis_tsys_gain)

tb.open(vis_tsys_gain, nomodify=False)
nrows = tb.nrows()
tb.removerows(range(nrows))
tb.putkeyword("MSName", vis) 
tb.flush()
tb.close()


startrow = 0
startrow_gcal = 0
for iant in iants:
    ### read the WVR data 
    tb.open(vis)
    spw_WVR = 4
    ddid = spw_WVR
    scan_exclude = list(scan_checksource)
    dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID==%d && SCAN_NUMBER not in %s'%(iant,iant,ddid,scan_exclude))
    WVR = np.real(dat.getcol('DATA'))
    WVR_avg = np.mean(WVR, axis=(0,1))
    WVR_sinchan = WVR[0][chan_WVR]
    WVR_time = dat.getcol('TIME')
    WVR_scans = dat.getcol('SCAN_NUMBER')
    WVR_field = dat.getcol('FIELD_ID')
    WVR_flag = dat.getcol('FLAG')
    tb.close()

    ## exclude the hot and cold load in the WVR measurement
    WVR_sinchan[np.where(WVR_sinchan>200)] = np.nan

    ## rebin the WVR for every 10 seconds.

    WVR_sinchan_binned, WVR_time_binned = rebin_time(WVR_sinchan, WVR_time, timebin=10)
    WVR_scans_temp = WVR_scans.astype(float) 
    WVR_scans_binned  = rebin_time(WVR_scans_temp, WVR_time, timebin=10, method='counts')[0]
    WVR_scans_binned[np.isnan(WVR_scans_binned)] = -1
    WVR_scans_binned = WVR_scans_binned.astype(int)

    WVR_field_temp = WVR_field.astype(float)
    WVR_field_binned  = rebin_time(WVR_field_temp, WVR_time, timebin=10, method='counts')[0]
    WVR_field_binned[np.isnan(WVR_field_binned)] = -1
    WVR_field_binned = WVR_field_binned.astype(int)

    ## remove the nan values in the rebinned data
    WVR_time_binned = WVR_time_binned[~np.isnan(WVR_sinchan_binned)]
    WVR_scans_binned = WVR_scans_binned[~np.isnan(WVR_sinchan_binned)]
    WVR_field_binned = WVR_field_binned[~np.isnan(WVR_sinchan_binned)]
    WVR_sinchan_binned = WVR_sinchan_binned[~np.isnan(WVR_sinchan_binned)]
     
    ## classify WVR data into different types of observation
    elements = WVR_scans_binned

    test_elements = np.array(list(scan_phase)+list(np.intersect1d((scan_phase-1), scan_ATM)))
    isin_phase_WVR = array_isin(elements, test_elements)
    WVR_phase = WVR_sinchan_binned[isin_phase_WVR]; time_WVR_phase = WVR_time_binned[isin_phase_WVR]

    test_elements = np.array(list(scan_sci)+list(np.intersect1d((scan_sci-1), scan_ATM)))
    isin_sci_WVR = array_isin(elements, test_elements)
    WVR_sci = WVR_sinchan_binned[isin_sci_WVR]; time_WVR_sci = WVR_time_binned[isin_sci_WVR]

    test_elements = np.array(list(scan_bpass)+list(np.intersect1d((scan_bpass-1), scan_ATM)))
    isin_bpass_WVR = array_isin(elements, test_elements)
    WVR_bpass = WVR_sinchan_binned[isin_bpass_WVR]; time_WVR_bpass = WVR_time_binned[isin_bpass_WVR]

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

    Tsys = average_Tsys(Tsys_spectrum, average_spw=True)
    Trx = average_Tsys(Trx_spectrum, average_spw=True)
    Tsky = average_Tsys(Tsky_spectrum, average_spw=True)

    ## select Tsys from a single spectral window
    if average_spw == False:
        Tsys_sinspw = select_spw_Tsys(Tsys, spws, spw_Tsys)
        Trx_sinspw = select_spw_Tsys(Trx, spws, spw_Tsys)
        Tsky_sinspw = select_spw_Tsys(Tsky, spws, spw_Tsys)
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

    ## match the system temperature with different observed data types 
    elements = scan_ATM + 1

    test_elements = scan_sci
    isin_sci = array_isin(elements, test_elements)
    Tsys_sci = Tsys_sinspw[isin_sci]
    Trx_sci = Trx_sinspw[isin_sci]
    Tsky_sci = Tsky_sinspw[isin_sci]
    time_Tsys_sci = time_Tsys[isin_sci]; dur_Tsys_sci = dur_Tsys[isin_sci]
    time_Tsys_sci_avg = np.mean(time_Tsys_sci, axis=1)

    test_elements = scan_phase
    isin_phase = array_isin(elements, test_elements)
    Tsys_phase = Tsys_sinspw[isin_phase]
    Trx_phase = Trx_sinspw[isin_phase]
    Tsky_phase = Tsky_sinspw[isin_phase]
    time_Tsys_phase = time_Tsys[isin_phase]; dur_Tsys_phase = dur_Tsys[isin_phase]
    time_Tsys_phase_avg = np.mean(time_Tsys_phase, axis=1)

    test_elements = scan_bpass
    isin_bpass = array_isin(elements, test_elements)
    Tsys_bpass = Tsys_sinspw[isin_bpass]
    Trx_bpass = Trx_sinspw[isin_bpass]
    Tsky_bpass = Tsky_sinspw[isin_bpass]
    time_Tsys_bpass = time_Tsys[isin_bpass]
    dur_Tsys_bpass = dur_Tsys[isin_bpass]
    time_Tsys_bpass_avg = np.mean(time_Tsys_bpass, axis=1)

    ### normalize the WVR data based on the start of Tsys

    normScans = [phasenormScan, scinormScan, bpassnormScan]

    phase_ind0 = find_nearest(WVR_time_binned,
                    time_Tsys_sci_avg[phasenormScan])
    sci_ind0 = find_nearest(WVR_time_binned, 
                    time_Tsys_sci_avg[scinormScan])
    bpass_ind0 = find_nearest(WVR_time_binned, 
                    time_Tsys_bpass_avg[bpassnormScan])
    WVR_phase_norm = WVR_phase / WVR_sinchan_binned[phase_ind0]
    WVR_sci_norm = WVR_sci / WVR_sinchan_binned[sci_ind0]
    WVR_bpass_norm = WVR_bpass / WVR_sinchan_binned[bpass_ind0]

    ## create a normalized WVR
    WVR_norm_binned = np.full(np.shape(WVR_sinchan_binned), np.nan)
    WVR_norm_binned[isin_sci_WVR] = WVR_sci_norm
    WVR_norm_binned[isin_bpass_WVR] = WVR_bpass_norm
    WVR_norm_binned[isin_phase_WVR] = WVR_phase_norm

    ## write the normalized WVR data into a gaintable.  
    tb.open(vis_tsys_gain, nomodify=False)
    gcal_time = np.tile(WVR_time_binned, 4)
    gcal_data = np.tile(WVR_norm_binned, 4)[np.newaxis, np.newaxis,:] 
    tb.addrows(len(gcal_time))
    tb.putcol('TIME', gcal_time, startrow_gcal)
    tb.putcol('FIELD_ID', np.tile(WVR_field_binned,4), startrow_gcal)
    tb.putcol('SPECTRAL_WINDOW_ID', np.repeat(np.unique(spws), len(WVR_time_binned)), startrow_gcal)
    tb.putcol('ANTENNA1', np.full(np.shape(gcal_time), iant), startrow_gcal)
    tb.putcol('ANTENNA2', np.full(np.shape(gcal_time), -1), startrow_gcal)
    tb.putcol('INTERVAL', np.full(np.shape(gcal_time), 0), startrow_gcal)
    tb.putcol('SCAN_NUMBER', np.tile(WVR_scans_binned, 4), startrow_gcal)
    tb.putcol('OBSERVATION_ID', np.full(np.shape(gcal_time),0), startrow_gcal)
    tb.putcol('CPARAM', gcal_data, startrow_gcal)
    tb.putcol('PARAMERR', np.full(np.shape(gcal_data), 0), startrow_gcal)
    tb.putcol('FLAG', np.full(np.shape(gcal_data), False), startrow_gcal)
    tb.putcol('SNR', np.full(np.shape(gcal_data), 1), startrow_gcal)
    tb.flush()
    tb.close()

    startrow_gcal = startrow_gcal + len(gcal_time)
    ### extrapolate the Tsys based on the start Tsys and WVR data

    ## match the system temperature with different observed data types
    elements = scan_ATM + 1

    test_elements = scan_phase
    isin_phase = array_isin(elements, test_elements)
    Tsys_phase = Tsys_sinspw[isin_phase]
    Trx_phase = Trx_sinspw[isin_phase]
    Tsky_phase = Tsky_sinspw[isin_phase]
    time_Tsys_phase = time_Tsys[isin_phase]; dur_Tsys_phase = dur_Tsys[isin_phase]
    time_Tsys_phase_avg = np.mean(time_Tsys_phase, axis=1)

    test_elements = scan_sci
    isin_sci = array_isin(elements, test_elements)
    Tsys_sci = Tsys_sinspw[isin_sci]
    Trx_sci = Trx_sinspw[isin_sci]
    Tsky_sci = Tsky_sinspw[isin_sci]
    time_Tsys_sci = time_Tsys[isin_sci]; dur_Tsys_sci = dur_Tsys[isin_sci]
    time_Tsys_sci_avg = np.mean(time_Tsys_sci, axis=1)

    test_elements = scan_bpass
    isin_bpass = array_isin(elements, test_elements)
    Tsys_bpass = Tsys_sinspw[isin_bpass]
    Trx_bpass = Trx_sinspw[isin_bpass]
    Tsky_bpass = Tsky_sinspw[isin_bpass]
    time_Tsys_bpass = time_Tsys[isin_bpass]
    dur_Tsys_bpass = dur_Tsys[isin_bpass]
    time_Tsys_bpass_avg = np.mean(time_Tsys_bpass, axis=1)

    ## extrapolate Tsys spectrum
    tb.open(vis_tsys_in)
    dat = tb.query('ANTENNA1==%d'%(iant))
    Tsys_spec_orig = dat.getcol('FPARAM')
    tb.close()
    # 3 types of observations (bpass and sci) and 4 spws. 
    Tsys_spec_ext = np.full(np.shape(Tsys_spectrum)[0:2]+(3*4,), np.nan)
    # calculate the indexes to extract from the original tsys table
    isin_extract = np.tile(np.array([isin_bpass[0][bpassnormScan],
                    isin_phase[0][phasenormScan], 
                    isin_sci[0][scinormScan]]),4)
    for i, value in enumerate(isin_extract):
        isin_extract[i] = int(i/3)*len(time_Tsys) + value
    
    for i in range(4):
        isin_sci_ext = isin_sci[0] + i * len(time_Tsys)
        isin_phase_ext = isin_phase[0] + i * len(time_Tsys)
        isin_bpass_ext = isin_bpass[0] + i * len(time_Tsys)
        Tsys_sci_ext = Tsys_spec_orig[:,:,isin_sci_ext[scinormScan]]
        Tsys_spec_ext[:,:,(2+3*i)] = Tsys_sci_ext
        Tsys_phase_ext = Tsys_spec_orig[:,:,isin_phase_ext[phasenormScan]]
        Tsys_spec_ext[:,:,(1+3*i)] = Tsys_phase_ext
        Tsys_bpass_ext = Tsys_spec_orig[:,:,isin_bpass_ext[bpassnormScan]] 
        Tsys_spec_ext[:,:,(3*i)] = Tsys_bpass_ext

    ## write a new Tsys into the alternative Tsys table
    # copy the information from .tsys table
    tb.open(vis_tsys_in)
    dat = tb.query('ANTENNA1==%d'%(iant))
    time_Tsys3 = dat.getcol('TIME')[isin_extract]
    field_Tsys3 = dat.getcol('FIELD_ID')[isin_extract]
    spws_Tsys3 = dat.getcol('SPECTRAL_WINDOW_ID')[isin_extract]
    scans_Tsys3 = dat.getcol('SCAN_NUMBER')[isin_extract]
    flag_Tsys3 = dat.getcol('FLAG')[:,:,isin_extract]
    snr_Tsys3 = dat.getcol('SNR')[:,:,isin_extract]
    paramerr_Tsys3 = dat.getcol('PARAMERR')[:,:,isin_extract]
    tb.close()

    tb.open(vis_tsys_out, nomodify=False)
    tb.addrows(len(time_Tsys3))
    tb.putcol('TIME',time_Tsys3,startrow) 
    tb.putcol('FIELD_ID',field_Tsys3,startrow) 
    tb.putcol('SPECTRAL_WINDOW_ID',spws_Tsys3, startrow) 
    tb.putcol('ANTENNA1', np.full(np.shape(time_Tsys3), iant), startrow)
    tb.putcol('ANTENNA2', np.full(np.shape(time_Tsys3), -1), startrow)
    tb.putcol('INTERVAL', np.full(np.shape(time_Tsys3), 0), startrow) 
    tb.putcol('SCAN_NUMBER', scans_Tsys3, startrow)
    tb.putcol('OBSERVATION_ID', np.full(np.shape(time_Tsys3), 0), startrow) 
    tb.putcol('FPARAM', Tsys_spec_ext, startrow) 
    tb.putcol('PARAMERR', paramerr_Tsys3, startrow) 
    tb.putcol('FLAG', flag_Tsys3, startrow) 
    tb.putcol('SNR', snr_Tsys3, startrow)
    tb.flush()
    tb.close()
    
    startrow = startrow + len(time_Tsys3)

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

