import numpy as np
import matplotlib.pyplot as plt

###########################################################
# basic parameters

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

iant = 0 # antenna id
chan_WVR = 3 # WVR channels
spw_Tsys = 17 # Tsys spectral window
average_spw = True
if average_spw == True:
    spw_Tsys = 'avg'

scan_ATM = np.array([2,5,8,10, 12, 16,18, 20, 24, 26, 28, 32, 34])
scan_phase = np.array([6,11,14,19,22,27,30,35]) 
scan_checksource = np.array([7, 15, 23, 31])
scan_bpass = np.array([3]) 
scan_sci = np.array([7,9,13,17,21,25,29,33])

keywords_title = 'ant '+str(iant)+' WVR '+str(chan_WVR)+' Tsys spw '+str(spw_Tsys)
keywords_filename = '_ant'+str(iant)+'_WVR'+str(chan_WVR)+'_Tsys_spw'+str(spw_Tsys)

###########################################################
# functions

def find_nearest(array, value):
    array = np.asarray(array)
    idx = np.nanargmin((np.abs(array - value)))

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
        shape = (len(spw_unique), len(Tsys)/len(spw_unique))
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

                                                        
###########################################################
# main program

## read the autocorrelation data
tb.open(vis)
spw_autCorr = [18,20,22,24]
ddid = spw_autCorr
scan_exclude = list(scan_ATM) + list(scan_phase)
dat = tb.query('ANTENNA1==%d && ANTENNA2==%d && DATA_DESC_ID in %s && SCAN_NUMBER not in %s'%(iant,iant,spw_autCorr, scan_exclude))
AutCorr = np.real(dat.getcol('DATA'))
AutCorr_avg = np.mean(AutCorr, axis=(0, 1))
AutCorr_time = dat.getcol('TIME')
AutCorr_spws = dat.getcol('DATA_DESC_ID')
tb.close()

AutCorr_temp = np.copy(AutCorr_avg)
AutCorr_temp[np.where(AutCorr_spws!=18)] = np.nan
AutCorr_spw18 = AutCorr_temp[~np.isnan(AutCorr_temp)]
AutCorr_time_spw18 = AutCorr_time[~np.isnan(AutCorr_temp)]

## read the WVR data 
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

# exclude the hot and cold load in the WVR measurement
WVR_time[np.where(WVR_sinchan>200)] = np.nan
WVR_sinchan[np.where(WVR_sinchan>200)] = np.nan

# classify WVR data into different types of observation
elements = WVR_scans

test_elements = np.array(list(scan_phase)+list(np.intersect1d((scan_phase-1), scan_ATM)))
isin = array_isin(elements, test_elements)
WVR_phase = WVR_sinchan[isin]; time_WVR_phase = WVR_time[isin]

test_elements = np.array(list(scan_sci)+list(np.intersect1d((scan_sci-1), scan_ATM)))
isin = array_isin(elements, test_elements)
WVR_sci = WVR_sinchan[isin]; time_WVR_sci = WVR_time[isin]

test_elements = np.array(list(scan_bpass)+list(np.intersect1d((scan_bpass-1), scan_ATM)))
isin = array_isin(elements, test_elements)
WVR_bpass = WVR_sinchan[isin]; time_WVR_bpass = WVR_time[isin]

## read the Tsys
tb.open(vis+'/SYSCAL')
tb3 = tb.query('ANTENNA_ID==%d'%(iant))
Tsys_spectrum = tb3.getcol('TSYS_SPECTRUM')
Trx_spectrum = tb3.getcol('TRX_SPECTRUM')
Tsky_spectrum = tb3.getcol('TSKY_SPECTRUM')
spws = tb3.getcol('SPECTRAL_WINDOW_ID')
time = tb3.getcol('TIME') 
tb.close()
print(spws)
# Tsys spws are 17, 19, 21, 23, which corresponds to autocorrelation spws of 16, 18, 20, 22

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

# match the system temperature with different observed data types
elements = scan_ATM + 1

test_elements = scan_phase
isin_phase = array_isin(elements, test_elements) 
Tsys_phase = Tsys_sinspw[isin_phase]
Trx_phase = Trx_sinspw[isin_phase]
Tsky_phase = Tsky_sinspw[isin_phase]
time_Tsys_phase = time_Tsys[isin_phase]; dur_Tsys_phase = dur_Tsys[isin_phase]

test_elements = scan_sci
isin_sci = array_isin(elements, test_elements)
Tsys_sci = Tsys_sinspw[isin_sci]
Trx_sci = Trx_sinspw[isin_sci]
Tsky_sci = Tsky_sinspw[isin_sci]
time_Tsys_sci = time_Tsys[isin_sci]; dur_Tsys_sci = dur_Tsys[isin_sci]

test_elements = scan_bpass
isin_bpass = array_isin(elements, test_elements)
Tsys_bpass = Tsys_sinspw[isin_bpass]
Trx_bpass = Trx_sinspw[isin_bpass]
Tsky_bpass = Tsky_sinspw[isin_bpass]
time_Tsys_bpass = time_Tsys[isin_bpass]
dur_Tsys_bpass = dur_Tsys[isin_bpass]

## match the autocorrelation time with ATM cal time.
indexes = []
for time_scan in time_Tsys:
    index = find_nearest(AutCorr_time_spw18, time_scan[-1])
    indexes.append(index)

## ignore the Tsys for phase cal.
# Tsys_sinspw = np.copy(Tsys_spw17) 
# for i, Tsys in enumerate(Tsys_sinspw):
#     if np.abs(time_Tsys[i][-1]-AutCorr_time_spw18[indexes[i]]) > 20:
#         Tsys_sinspw[i] = np.nan

# match the Tsys in phase cal, science observation and bandpass, normalized to each Tsys

# Tsys_ext = np.full(np.shape(AutCorr_time_spw18), np.nan)
# for i, index in enumerate(indexes):
#     if i == (len(indexes) - 1):
#         Tsys_ext[indexes[i]:] = Tsys_sinspw[i] *\
#             AutCorr_spw18[index:] / AutCorr_spw18[index]
#     else:
#         Tsys_ext[indexes[i]:indexes[i+1]] = Tsys_sinspw[i] *\
#             AutCorr_spw18[indexes[i]:indexes[i+1]] / AutCorr_spw18[index]

# Tsys_ext[:indexes[4]] = np.nan
# Tsys_ext[indexes[5]:] = np.nan

# ## match the autocorrelation time with ATM cal time.
# Tsys_ext = Tsys_sinspw[1] * AutCorr_spw26 / AutCorr_spw26[0]

# pick one section
# isec = 6
# time_Tsys = time_Tsys[isec:(isec+2)]; Tsys_sinspw = Tsys_sinspw[isec:(isec+2)]
# Tsys_ext[:indexes[isec]] = np.nan
# Tsys_ext[indexes[isec+1]:] = np.nan

### Normalize only once for the start of Tsys
index_nonan = np.where(~np.isnan(Tsys_sinspw))
i = index_nonan[0][1]
Tsys_ext1 = Tsys_sinspw[i] * AutCorr_spw18 / AutCorr_spw18[indexes[i]]

### normalize to WVR once
index_nonan = np.where(~np.isnan(Tsys_sinspw))
i = index_nonan[0][1]
index = find_nearest(WVR_time, time_Tsys[i][0])
Tsys_ext2 = Tsys_sinspw[i] * WVR_sinchan / WVR_sinchan[index]

# check the normalized Tsys and autocorrelation data
# Tsys_normalized = Tsys_sinspw / Tsys_sinspw[i]
# AutCorr_spw18_norm = AutCorr_spw18 / AutCorr_spw18[indexes[i]]
# fig =  plt.figure()
# plt.scatter(time_Tsys[:,0], Tsys_normalized, color='blue', label='normalized Tsys')
# plt.scatter(AutCorr_time_spw18, AutCorr_spw18_norm, color='red', label='normalized autocorrelation')
# plt.legend(loc='lower right')
# plt.xlabel('time (s)')
# plt.savefig('Tsys_autocorrelation_check.pdf')

# # plot the extrapolated Tsys based on the autocorrelation data
# fig = plt.figure() 
# for i, time in enumerate(time_Tsys):
#     plt.plot([time_Tsys[i][0], time_Tsys[i][-1]], 
#              [Tsys_sinspw[i], Tsys_sinspw[i]], color='red', linewidth=5)
# # plt.scatter(AutCorr_time_spw18, Tsys_ext, marker='.', label='Extrapolated from each Tsys')
# plt.scatter(AutCorr_time_spw18, Tsys_ext1, marker='.', color='blue', label='Extrapolated from start Tsys')
# plt.title('Ant 0, Tsys spw 17, autocorrelation spw 18')
# plt.xlabel('time (s)')
# plt.ylabel('Tsys (K)')
# # plt.ylim(bottom=1300)
# plt.legend(loc='lower right')
# plt.savefig('Tsys_extrapolate_autocorrelation_band10.pdf', bbox_incehs='tight')

# nomralized WVR and Tsys data

# normalize WVR data 
phase_ind0 = find_nearest(WVR_time, time_Tsys_phase[0][0])
sci_ind0 = find_nearest(WVR_time, time_Tsys_sci[0][0])
bpass_ind0 = find_nearest(WVR_time, time_Tsys_bpass[0][0])
WVR_phase_norm = WVR_phase / WVR_sinchan[phase_ind0]
WVR_sci_norm = WVR_sci / WVR_sinchan[sci_ind0]
WVR_bpass_norm = WVR_bpass / WVR_sinchan[bpass_ind0]

# normalize Tsys
Tsys_phase_norm = Tsys_phase / Tsys_phase[0]
Tsys_sci_norm = Tsys_sci / Tsys_sci[0]
Tsys_bpass_norm = Tsys_bpass / Tsys_bpass[0]
Tsys_norm = normalize_Tsys(Tsys_sinspw, isin_phase, isin_sci, isin_bpass)

Trx_phase_norm = Trx_phase / Trx_phase[0]
Trx_sci_norm = Trx_sci / Trx_sci[0]
Trx_bpass_norm = Trx_bpass / Trx_bpass[0]
Trx_norm = normalize_Tsys(Trx_sinspw, isin_phase, isin_sci, isin_bpass)

Tsky_phase_norm = Tsky_phase / Tsky_phase[0]
Tsky_sci_norm = Tsky_sci / Tsky_sci[0]
Tsky_bpass_norm = Tsky_bpass / Tsky_bpass[0]
Tsky_norm = normalize_Tsys(Tsky_sinspw,isin_phase,isin_sci,isin_bpass)

## plot the normalized Tsys and WVR data
fig = plt.figure()
plt.title(keywords_title)
plt.scatter(time_WVR_phase, WVR_phase_norm, color='green', marker='.', label='WVR phase cal')
plt.scatter(time_WVR_sci, WVR_sci_norm, color='royalblue', marker='.', label='WVR science')
plt.scatter(time_WVR_bpass, WVR_bpass_norm, color='orange', marker='.', label='WVR bandpass')
# plt.scatter(time_Tsys_phase[:,0], Tsys_phase_norm, s=dur_Tsys_phase,color='red',linewidth=5,marker='_', label='Tsys normalized')
# plt.scatter(time_Tsys_sci[:,0], Tsys_sci_norm, s=dur_Tsys_sci,color='red',linewidth=5,marker='_')
# plt.scatter(time_Tsys_bpass[:,0], Tsys_bpass_norm, s=dur_Tsys_bpass,color='red',linewidth=5,marker='_')
# plt.scatter(time_Tsys_phase[:,0], Trx_phase_norm, s=dur_Tsys_phase,color='magenta',linewidth=5,marker='_',label='Trx normalized')
# plt.scatter(time_Tsys_sci[:,0], Trx_sci_norm, s=dur_Tsys_sci,color='magenta',linewidth=5,marker='_')
# plt.scatter(time_Tsys_bpass[:,0], Trx_bpass_norm, s=dur_Tsys_bpass,color='magenta',linewidth=5,marker='_')
# plt.scatter(time_Tsys_phase[:,0], Tsky_phase_norm, s=dur_Tsys_phase,color='black',linewidth=5,marker='_',label='Tsky normalized')
# plt.scatter(time_Tsys_sci[:,0], Tsky_sci_norm, s=dur_Tsys_sci,color='black',linewidth=5,marker='_')
# plt.scatter(time_Tsys_bpass[:,0], Tsky_bpass_norm, s=dur_Tsys_bpass,color='black',linewidth=5,marker='_')
plt.scatter(time_Tsys[:,0], Trx_norm, s=dur_Tsys,color='magenta',linewidth=5,marker='_',label='Trx normalized')
plt.scatter(time_Tsys[:,0], Tsky_norm, s=dur_Tsys,color='black',linewidth=5,marker='_',label='Tsky normalized')
plt.scatter(time_Tsys[:,0], Tsys_norm, s=dur_Tsys ,color='red',linewidth=5,marker='_', label='Tsys normalized')

plt.ylim(bottom=0.9)
plt.legend(loc='lower left')
plt.savefig('Tsys_WVR_normalized'+keywords_filename+'.pdf')

# plot the extrapolated Tsys based on the WVR data
fig = plt.figure()
for i, time in enumerate(time_Tsys):
    plt.plot([time_Tsys[i][0], time_Tsys[i][-1]],
             [Tsys_sinspw[i], Tsys_sinspw[i]], color='red', linewidth=5)
plt.scatter(WVR_time, Tsys_ext2, marker='.', color='blue', label='Extrapolated from start Tsys')
plt.title(keywords_title)
plt.xlabel('time (s)')
plt.ylabel('Tsys (K)')
plt.legend(loc='lower right')
plt.savefig('Tsys_extrapolate_WVR_band10'+keywords_filename+'.pdf', bbox_incehs='tight')
