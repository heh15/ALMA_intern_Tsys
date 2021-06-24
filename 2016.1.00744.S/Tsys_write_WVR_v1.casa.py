import time

###########################################################
# basic settings

vis = 'uid___A002_Xbf792a_X14cc.ms'

iants = range(41)
# iants = range(1)

chan_WVR = 1 # WVR channels
spw_Tsys = 17 # Tsys spectral window
average_spw = True

scan_ATM = np.array([2, 5, 8, 10, 15, 17, 22, 24, 29, 31])
scan_phase = np.array([6, 11, 13, 18, 20, 25, 27, 32, 34])
scan_checksource = np.array([7, 14, 21, 28])
scan_bpass = np.array([3])
scan_sci = np.array([9, 12, 16, 19, 23, 26, 30, 33])

scinormScan = 0
phasenormScan = 0
bpassnormScan = 0

time_avg = 10 

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

###########################################################
# main program
start = time.time()

### create the alternative Tsys tables
vis_tsys_in = vis + '.tsys'
tb.open(vis+'.tsys')
tabdesc = tb.getdesc()
dminfo  = tb.getdminfo()
info = tb.info()
tb.close()

vis_tsys_out = vis.replace('.ms', '_v1.ms.tsys')
rmtables(vis_tsys_out)
os.system('cp -r '+vis_tsys_in+' '+vis_tsys_out)

tb.open(vis_tsys_out, nomodify=False)
nrows = tb.nrows()
tb.removerows(range(nrows))
tb.flush()
tb.close()

startrow = 0
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
    tb.close()

    ## exclude the hot and cold load in the WVR measurement
    WVR_time[np.where(WVR_sinchan>200)] = np.nan
    WVR_sinchan[np.where(WVR_sinchan>200)] = np.nan

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

    phase_ind0 = find_nearest(WVR_time, time_Tsys_sci_avg[phasenormScan])
    sci_ind0 = find_nearest(WVR_time, time_Tsys_sci_avg[scinormScan])
    bpass_ind0 = find_nearest(WVR_time, time_Tsys_bpass_avg[bpassnormScan])
    WVR_phase_norm = WVR_phase / WVR_sinchan[phase_ind0]
    WVR_sci_norm = WVR_sci / WVR_sinchan[sci_ind0]
    WVR_bpass_norm = WVR_bpass / WVR_sinchan[bpass_ind0]

    ## write the WVR data into a calibration table
    # should be similar to fluxcal table

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

    ## average the matched WVR data by the start of 10s
    sci_ind = find_nearest(time_WVR_sci, time_Tsys_sci_avg)
    phase_ind = find_nearest(time_WVR_phase, time_Tsys_phase_avg) 
    bpass_ind = find_nearest(time_WVR_bpass, time_Tsys_bpass_avg)

    lowerTimes = time_WVR_sci[sci_ind]
    upperTimes = time_WVR_sci[sci_ind] + time_avg
    WVR_matchedSci, indices_matchedSci = filter_data(WVR_sci_norm, time_WVR_sci, lowerTimes, upperTimes)
    WVR_Sciavg = np.array([np.mean(data) for data in WVR_matchedSci])

    lowerTimes = time_WVR_phase[phase_ind]
    upperTimes = time_WVR_phase[phase_ind] + time_avg
    WVR_matchedPhase, indices_matchedPhase = filter_data(WVR_phase_norm, time_WVR_phase, lowerTimes, upperTimes)
    WVR_Phaseavg = np.array([np.mean(data) for data in WVR_matchedPhase])

    lowerTimes = time_WVR_bpass[bpass_ind]
    upperTimes = time_WVR_bpass[bpass_ind] + time_avg
    WVR_matchedBpass, indices_matchedBpass = filter_data(WVR_bpass_norm, time_WVR_bpass, lowerTimes, upperTimes)
    WVR_Bpassavg = np.array([np.mean(data) for data in WVR_matchedBpass])

    ## extrapolate Tsys spectrum
    tb.open(vis_tsys_in)
    dat = tb.query('ANTENNA1==%d'%(iant))
    Tsys_spec_orig = dat.getcol('FPARAM')
    tb.close()
    Tsys_spec_ext = np.full(np.shape(Tsys_spectrum), np.nan)
    for i in range(4):
        isin_sci_ext = isin_sci[0] + i * len(time_Tsys)
        isin_phase_ext = isin_phase[0] + i * len(time_Tsys)
        isin_bpass_ext = isin_bpass[0] + i * len(time_Tsys)
        Tsys_sci_ext = np.einsum('ij, k->ijk',
                Tsys_spec_orig[:,:,isin_sci_ext[scinormScan]], WVR_Sciavg)
        Tsys_spec_ext[:,:,isin_sci_ext] = Tsys_sci_ext
        Tsys_phase_ext = np.einsum('ij, k->ijk', 
                Tsys_spec_orig[:,:,isin_phase_ext[phasenormScan]],WVR_Phaseavg)
        Tsys_spec_ext[:,:,isin_phase_ext] = Tsys_phase_ext
        Tsys_bpass_ext = np.einsum('ij, k->ijk',
                Tsys_spec_orig[:,:,isin_bpass_ext[bpassnormScan]], WVR_Bpassavg)
        Tsys_spec_ext[:,:,isin_bpass_ext] = Tsys_bpass_ext

    ## write a new Tsys into the alternative Tsys table
    # copy the information from .tsys table
    tb.open(vis_tsys_in)
    dat = tb.query('ANTENNA1==%d'%(iant))
    time_Tsys1 = dat.getcol('TIME')
    field_Tsys1 = dat.getcol('FIELD_ID')
    spws_Tsys1 = dat.getcol('SPECTRAL_WINDOW_ID')
    scans_Tsys1 = dat.getcol('SCAN_NUMBER')
    flag_Tsys1 = dat.getcol('FLAG')
    snr_Tsys1 = dat.getcol('SNR')
    paramerr_Tsys1 = dat.getcol('PARAMERR')
    tb.close()

    tb.open(vis_tsys_out, nomodify=False)
    tb.addrows(len(time_Tsys1))
    tb.putcol('TIME',time_Tsys1,startrow) 
    tb.putcol('FIELD_ID',field_Tsys1,startrow) 
    tb.putcol('SPECTRAL_WINDOW_ID',spws_Tsys1, startrow) 
    tb.putcol('ANTENNA1', np.full(np.shape(time_Tsys1), iant), startrow)
    tb.putcol('ANTENNA2', np.full(np.shape(time_Tsys1), -1), startrow)
    tb.putcol('INTERVAL', np.full(np.shape(time_Tsys1), 0), startrow) 
    tb.putcol('SCAN_NUMBER', scans_Tsys1, startrow)
    tb.putcol('OBSERVATION_ID', np.full(np.shape(time_Tsys1), 0), startrow) 
    tb.putcol('FPARAM', Tsys_spec_ext, startrow) 
    tb.putcol('PARAMERR', paramerr_Tsys1, startrow) 
    tb.putcol('FLAG', flag_Tsys1, startrow) 
    tb.putcol('SNR', snr_Tsys1, startrow)
    tb.flush()
    tb.close()
    
    startrow = startrow + len(time_Tsys1)

stop = time.time()
count_time(stop, start)
