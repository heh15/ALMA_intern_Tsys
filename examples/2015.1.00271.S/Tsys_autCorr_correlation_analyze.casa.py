import pickle
import numpy as np
import matplotlib.pyplot as plt
import copy

###########################################################
# basic settings

vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'
filename = 'Tsys_autCorr_correlation_spwautCorr19_spwTsysavg_avgTime10.pkl'

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
    Tsys_table = pickle.load(pickle_file)

# information of the data
info = Tsys_table['info']
info_txts = copy.deepcopy(info)
for key in info_txts.keys():
    info_txts[key] = str(info_txts[key])
keywords_title = ', '.join('{}  {}'.format(key, value) for key, value in info.items())
keywords_filename = '_'.join('{}{}'.format(key, value) for key, value in info.items())
keywords_filename = keywords_filename.replace(' ','')

iants = Tsys_table['iant']

obs_type = Tsys_table['obs_type']
obs_type = obs_type.astype(str)
isin_sci = np.where(obs_type=='science')
iants_sci = iants[isin_sci]

idx_iant = np.isin(iants, np.array([36]))

time_Tsys = Tsys_table['time_Tsys'] 
tau_mean = Tsys_table['tau_mean']
autCorr_norms = Tsys_table['autCorr_norms']
Tsys_norms = Tsys_table['Tsys_norm']
Tsky_norms = Tsys_table['Tsky_norm']

Tsys = Tsys_table['Tsys']
autCorr_means = Tsys_table['autCorr_means']

autCorr_norms[np.where(iants==30)] = np.nan
autCorr_means[np.where(iants==30)] = np.nan
autCorr_norms[np.where(iants==36)] = np.nan
autCorr_means[np.where(iants==36)] = np.nan

autCorr_norms_tau = normalize_array(autCorr_norms*np.exp(-tau_mean), iants, obs_type)

err_rel = np.nanmean(np.abs(Tsys_norms - autCorr_norms)/autCorr_norms)
err_rel2 = np.nanmean(np.abs(Tsky_norms - autCorr_norms)/autCorr_norms)

#############################
# plot the Tsys vs autCorr


fig = plt.figure()
ax = plt.subplot(111)

# create color dictionary for the scatter plot
color_dict = { 'phase':'green', 'science':'blue', 'bandpass':'orange'}
color_dict["Mean relative error "+str(round(err_rel,4))] = 'black'
legendhandle = [plt.plot([], marker="o", ls="", color=color)[0] for color in list(color_dict.values())]

# plot the scatter plot
sc = ax.scatter(Tsys_norms, autCorr_norms, c=map_series_by_dict(obs_type, color_dict))

# plot the 1-to-1 line
lower=max(ax.set_xlim()[0], ax.set_ylim()[0])
upper=min(ax.set_xlim()[1], ax.set_ylim()[1])
ax.plot([lower, upper],[lower,upper],ls='--', color='black')

# title
title = 'AutCorr vs Tsys, all ants '+keywords_title
plt.title(title)

# label
plt.xlabel('Normalized Tsys')
plt.ylabel('Normalized AutCorr')
plt.legend(loc='upper left', framealpha=0.5)
plt.legend(legendhandle,list(color_dict.keys()), loc='upper left', framealpha=0.5)
plt.savefig('Tsys_autCorr_correlation_band10'+keywords_filename+'.pdf', bbox_incehs='tight')


#############################
# plot the Tsys vs autCorr with optical depth correction

fig = plt.figure()
ax = plt.subplot(111)

# create color dictionary for the scatter plot
color_dict = { 'phase':'green', 'science':'blue', 'bandpass':'orange'}
color_dict["optical depth corrected"] = 'black'
legendhandle = [plt.plot([], marker="o", ls="", color=color)[0] for color in list(color_dict.values())]

# plot the scatter plot
sc = ax.scatter(Tsys_norms, autCorr_norms_tau, c=map_series_by_dict(obs_type, color_dict))

# plot the 1-to-1 line
lower=max(ax.set_xlim()[0], ax.set_ylim()[0])
upper=min(ax.set_xlim()[1], ax.set_ylim()[1])
ax.plot([lower, upper],[lower,upper],ls='--', color='black')

# title
title = 'AutCorr vs Tsys, all ants '+keywords_title
plt.title(title)

# label
plt.xlabel('Normalized Tsys')
plt.ylabel('Normalized AutCorr')
plt.legend(loc='upper left', framealpha=0.5)
plt.legend(legendhandle,list(color_dict.keys()), loc='upper left', framealpha=0.5)
plt.savefig('Tsys_autCorr_correlation_band10_opdepth'+keywords_filename+'.pdf', bbox_incehs='tight')


#############################
# plot the Tsys vs autCorr, comparing the optical depth effect

fig = plt.figure()
ax = plt.subplot(111)

sc = ax.scatter(Tsys_norms, autCorr_norms, color='blue',label='original')
sc1 = ax.scatter(Tsys_norms, autCorr_norms_tau, color='green',label='optical depth mod')

lower=max(ax.set_xlim()[0], ax.set_ylim()[0])
upper=min(ax.set_xlim()[1], ax.set_ylim()[1])
ax.plot([lower, upper],[lower,upper],ls='--', color='black')
plt.plot([], [], ' ', label="Mean relative error "+str(round(err_rel,3)))

plt.title('AutCorr vs Tsys'+keywords_title)
plt.xlabel('Normalized Tsys')
plt.ylabel('Normalized AutCorr')
plt.legend(loc='lower right', framealpha=0.5)


