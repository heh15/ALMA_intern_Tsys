import pickle
import numpy as np
import matplotlib.pyplot as plt

###########################################################
# basic settings

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'
# filename = 'WVR_gaintable_chanWVRavg_spwTsysavg_avgTime10.pkl'
filename = 'WVR_gaintable_chanWVR0_spwTsysavg_avgTime10.pkl'

filename2 = 'Tsys_WVR_correlation_chanWVRavg_spwTsysavg_avgTime10.pkl' 

bad_ants = np.array([30,36])

###########################################################
# functions

def map_series_by_dict(a, d):

    v = np.array(list(d.values()))
    k = np.array(list(d.keys()))
    sidx = k.argsort()
    out_ar = v[sidx[np.searchsorted(k,a,sorter=sidx)]]
    return out_ar

def normalize_array(array, iants, obs_type):

    array_norm = np.full(np.shape(array), fill_value=np.nan)
    iants_uq = np.unique(iants)
    obsType_uq = np.unique(obs_type)
    for iant in iants_uq:
        for obs in obsType_uq:
            conditions = ((iants == iant) & (obs_type==obs))
            indices = np.where(conditions)
            array_sub = array[indices]
            array_norm[indices] = array_sub / array_sub[0]

    return array_norm

###########################################################
# main program

with open (filename, 'rb') as pickle_file:
    WVR_table = pickle.load(pickle_file)

with open (filename2, 'rb') as pickle_file:
    Tsys_table = pickle.load(pickle_file)

# information of the data
info = WVR_table['info']

keywords_title = ', '.join('{}  {}'.format(key, value) for key, value in info.items())
keywords_filename = '_'.join('{}{}'.format(key, value) for key, value in info.items())
keywords_filename = keywords_filename.replace(' ','')

# input the data
iants_WVR = WVR_table['iant']
Tsys_exts = WVR_table['Tsys_exts']
WVR_time = WVR_table['WVR_time']
WVR_norms = WVR_table['WVR_norms']
Tsys_starts = WVR_table['Tsys_starts']
Tsys_origs = WVR_table['Tsys_origs'] 
obs_type_WVR = WVR_table['obs_type']
obs_type_WVR = obs_type_WVR.astype('str')

Tsys_exts[np.isin(iants_WVR, bad_ants)] = np.nan
Tsys_origs[np.isin(iants_WVR, bad_ants)] = np.nan

iants_Tsys = Tsys_table['iant']
Tsys = Tsys_table['Tsys']
time_Tsys = Tsys_table['time_Tsys']
obs_type_Tsys = Tsys_table['obs_type']
obs_type_Tsys = obs_type_Tsys.astype('str')

Tsys[np.isin(iants_Tsys, bad_ants)] = np.nan

#############################
# calculate the mean ratio between bandpass and science for 
# original and extrapolated Tsys. 
# Tsys_exts[np.isnan(Tsys_origs)] = np.nan
iants_WVR_sci = iants_WVR[np.where(obs_type_WVR=='science')]
iants_WVR_phase = iants_WVR[np.where(obs_type_WVR=='phase')]
iants_WVR_bpass = iants_WVR[np.where(obs_type_WVR=='bandpass')]

Tsys_exts_sci = Tsys_exts[np.where(obs_type_WVR=='science')]
Tsys_exts_phase = Tsys_exts[np.where(obs_type_WVR=='phase')]
Tsys_exts_bpass = Tsys_exts[np.where(obs_type_WVR=='bandpass')]
Tsys_origs_sci = Tsys_origs[np.where(obs_type_WVR=='science')]
Tsys_origs_phase = Tsys_origs[np.where(obs_type_WVR=='phase')]
Tsys_origs_bpass = Tsys_origs[np.where(obs_type_WVR=='bandpass')]

Tsys_sci = Tsys[np.where(obs_type_Tsys == 'science')] 

ratio1 = np.nanmean(Tsys_exts_sci) / np.nanmean(Tsys_origs_sci)
ratio2 = np.nanmean(Tsys_exts_bpass) / np.nanmean(Tsys_origs_bpass)
ratio3 = np.nanmean(Tsys_exts_phase) / np.nanmean(Tsys_origs_phase)
ratio4 = ratio1 / ratio2 /ratio3
ratio5 = np.nanmean(Tsys_exts) / np.nanmean(Tsys_origs)

ratio6 = np.nanmean(Tsys_exts_sci) / np.nanmean(Tsys_sci)


# ratio for individual antennas
iant = 10
ratio_sinant = np.nanmean(Tsys_exts_sci[np.where(iants_WVR_sci==iant)] / Tsys_origs_sci[np.where(iants_WVR_sci==iant)])
ratiop_sinant = np.nanmean(Tsys_exts_phase[np.where(iants_WVR_phase==iant)] / Tsys_origs_phase[np.where(iants_WVR_phase==iant)])

#############################
# plot Tsys vs time for a single antenna
iant = 10

fig = plt.figure()
plt.scatter(WVR_time[np.where(iants_WVR==iant)], Tsys_exts[np.where(iants_WVR==iant)],
           color='blue')
plt.scatter(WVR_time[np.where(iants_WVR==iant)], Tsys_origs[np.where(iants_WVR==iant)],
            color='red')
plt.scatter(time_Tsys[np.where(iants_Tsys==iant)], Tsys[np.where(iants_Tsys==iant)],
            color='green')
