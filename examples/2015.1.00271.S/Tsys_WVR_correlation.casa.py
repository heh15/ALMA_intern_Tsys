import numpy as np
import sys
import matplotlib.pyplot as plt
import time

sys.path.insert(0, '/home/heh15/research/toolkit')
# from casaFunctions import average_spws
# from casaFunctions import average_Tsys

############################################################
# basic parameters

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

chan_WVR = 2 # WVR channels
spw_Tsys = 19 # Tsys spectral window
average_spw = True
if average_spw == True:
    spw_Tsys = 'avg'

average_WVR = True
if average_WVR == True:
    chan_WVR = 'avg' 

scan_ATM = np.array([2,5,8,10, 12, 16,18, 20, 24, 26, 28, 32, 34])
scan_phase = np.array([6,11,14,19,22,27,30,35])
scan_checksource = np.array([7, 15, 23, 31])
scan_bpass = np.array([3])
scan_sci = np.array([7,9,13,17,21,25,29,33])

time_avg = 10

keywords_title = ' WVR '+str(chan_WVR)+' Tsys spw '+str(spw_Tsys)+' avgTime '+str(time_avg)
keywords_filename = '_WVR'+str(chan_WVR)+'_Tsys_spw'+str(spw_Tsys)+'_avgTime'+str(time_avg)

###########################################################
# functions

def find_nearest(array, values):
    array = np.asarray(array)
    idx = np.nanargmin((np.abs(array[:,np.newaxis] - values)), axis=0)

    return idx

def array_isin(element, test_elements):
   
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
        shape = (len(spw_unique), int(len(Tsys)/len(spw_unique)))
        Tsys_temp = np.full(shape, np.nan)
        for i, spw in enumerate(np.unique(spws)):
            Tsys_temp[i] = Tsys[np.where(spws==spw)]

        Tsys = np.mean(Tsys_temp, axis=0)

    return Tsys

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

def filter_data(data, time, lowerTimes, upperTimes):
    
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

iants = np.arange(0, 43, 1)
iants = np.delete(iants, np.argwhere(iants == 30)) # antenna 30 has weird Tsys values

WVR_Sciavgs = []
WVR_Bpassavgs = []
WVR_Phaseavgs = []
Tsys_sci_norms = []
Tsys_bpass_norms = []
Tsys_phase_norms = []

start = time.time()

for iant in iants:
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

    # select single channel for WVR
    if average_WVR == True:
        weights = 1/(0.5-(WVR[0]/275))**2
        WVR_sinchan = np.average(WVR[0], axis=0, weights=weights)
    else:
        WVR_sinchan = WVR[0][chan_WVR]

    # exclude the hot and cold load in the WVR measurement
    WVR_time[np.where(WVR_sinchan>200)] = np.nan
    WVR_sinchan[np.where(WVR_sinchan>200)] = np.nan

    # classify WVR data into different types of observation
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

    ## read the Tsys
    tb.open(vis+'/SYSCAL')
    tb3 = tb.query('ANTENNA_ID==%d'%(iant))
    Tsys_spectrum = tb3.getcol('TSYS_SPECTRUM')
    Trx_spectrum = tb3.getcol('TRX_SPECTRUM')
    Tsky_spectrum = tb3.getcol('TSKY_SPECTRUM')
    spws = tb3.getcol('SPECTRAL_WINDOW_ID')
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

    # time for the system temperature
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

    # match the system temperature with different observed data types
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

    ## normalize WVR and Tsys

    # normalize WVR data 
    phase_ind0 = find_nearest(WVR_time, time_Tsys_phase_avg[0])
    sci_ind0 = find_nearest(WVR_time, time_Tsys_sci_avg[0])
    bpass_ind0 = find_nearest(WVR_time, time_Tsys_bpass_avg[0])
    WVR_phase_norm = WVR_phase / WVR_sinchan[phase_ind0]
    WVR_sci_norm = WVR_sci / WVR_sinchan[sci_ind0]
    WVR_bpass_norm = WVR_bpass / WVR_sinchan[bpass_ind0]

    # normalize Tsys
    Tsys_phase_norm = Tsys_phase / Tsys_phase[0]
    Tsys_sci_norm = Tsys_sci / Tsys_sci[0]
    Tsys_bpass_norm = Tsys_bpass / Tsys_bpass[0]
    Tsys_norm = normalize_Tsys(Tsys_sinspw, isin_phase, isin_sci, isin_bpass)

    # Trx_phase_norm = Trx_phase / Trx_phase[0]
    Trx_sci_norm = Trx_sci / Trx_sci[0]
    Trx_bpass_norm = Trx_bpass / Trx_bpass[0]
    Trx_norm = normalize_Tsys(Trx_sinspw, isin_phase, isin_sci, isin_bpass)

    # Tsky_phase_norm = Tsky_phase / Tsky_phase[0]
    Tsky_sci_norm = Tsky_sci / Tsky_sci[0]
    Tsky_bpass_norm = Tsky_bpass / Tsky_bpass[0]
    Tsky_norm = normalize_Tsys(Tsky_sinspw,isin_phase,isin_sci,isin_bpass)

    ## match the Tsys with 30s WVR across the Tsys
    phase_ind = find_nearest(time_WVR_phase, time_Tsys_phase_avg) 
    sci_ind = find_nearest(time_WVR_sci, time_Tsys_sci_avg)
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

    WVR_Sciavgs.append(WVR_Sciavg)
    WVR_Bpassavgs.append(WVR_Bpassavg)
    WVR_Phaseavgs.append(WVR_Phaseavg)
    Tsys_sci_norms.append(Tsys_sci_norm)
    Tsys_bpass_norms.append(Tsys_bpass_norm)
    Tsys_phase_norms.append(Tsys_phase_norm)

stop = time.time()
count_time(stop, start)

WVR_Sciavgs = np.array(WVR_Sciavgs)
WVR_Phaseavgs = np.array(WVR_Phaseavgs)
WVR_Bpassavgs = np.array(WVR_Bpassavgs)
Tsys_sci_norms = np.array(Tsys_sci_norms)
Tsys_phase_norms = np.array(Tsys_phase_norms)
Tsys_bpass_norms = np.array(Tsys_bpass_norms)

WVR_avgs = np.array(list(WVR_Sciavgs.flatten())+list(WVR_Phaseavgs.flatten())+list(WVR_Bpassavgs.flatten()))
Tsys_norms = np.array(list(Tsys_sci_norms.flatten())+list(Tsys_phase_norms.flatten())+list(Tsys_bpass_norms.flatten()))

WVR_avgs[np.where(WVR_avgs==1)] = np.nan
Tsys_norms[np.where(Tsys_norms==1)] = np.nan

err_rel = np.nanmean(np.abs(Tsys_norms - WVR_avgs)/WVR_avgs)

fig = plt.figure()
ax = plt.subplot(111)

# create an iants array for the data
sc = ax.scatter(WVR_Sciavgs.flatten(), Tsys_sci_norms.flatten(), color='blue', label='science')
ax.scatter(WVR_Bpassavgs.flatten(), Tsys_bpass_norms.flatten(), color='orange', label='bandpass')
ax.scatter(WVR_Phaseavgs.flatten(), Tsys_phase_norms.flatten(), color='green', label='phase')

lower=max(ax.set_xlim()[0], ax.set_ylim()[0])
upper=min(ax.set_xlim()[1], ax.set_ylim()[1])
ax.plot([lower, upper],[lower,upper],ls='--', color='black')
plt.plot([], [], ' ', label="Mean relative error "+str(round(err_rel,3)))

plt.title(keywords_title)
plt.xlabel('Normalized WVR')
plt.ylabel('Normalized Tsys')
plt.legend(loc='upper left', framealpha=0.5)
plt.savefig('Tsys_WVR_correlation_band7'+keywords_filename+'.pdf', bbox_incehs='tight') 
