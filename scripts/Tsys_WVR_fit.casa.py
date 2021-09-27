'''
To fit the linear relation between the normalized WVR data with Tsys data
'''

###########################################################
# functions 

import pickle
import numpy as np

def normalize_array(array, iants, obs_type, normScans=[0,0,0]):

    array_norm = np.full(np.shape(array), fill_value=np.nan)
    iants_uq = np.unique(iants)
    obsType_uq = np.unique(obs_type)
    for iant in iants_uq:
        for i, obs in enumerate(obsType_uq):
            conditions = ((iants == iant) & (obs_type==obs))
            indices = np.where(conditions)
            array_sub = array[indices]
            array_norm[indices] = array_sub / array_sub[normScans[i]]

    return array_norm

###########################################################
# basic settings

filename = 'Tsys_WVR_matched_avgTime10.pkl'

WVR_chan = 3

normScans = [0,0,0]
normScans_txt = ''.join([str(i) for i in normScans])

fitfile = 'Tsys_WVR_fitted_WVRchan'+str(WVR_chan)+'_normScans'+\
        normScans_txt+'.pkl'

###########################################################
# main program

##  load the data
with open (filename, 'rb') as pickle_file:
    Tsys_table = pickle.load(pickle_file)

# basic information
iants = Tsys_table['iant']
obs_type = Tsys_table['obs_type']

# import the matched Tsys and WVR
WVR_means = Tsys_table['WVR_means'][:,WVR_chan]
Tsys = Tsys_table['Tsys']

## normalize Tsys and WVR data.
WVR_norms = normalize_array(WVR_means, iants, obs_type, normScans=normScans)

Tsys_norms = np.full(np.shape(Tsys), fill_value=np.nan)
for i in range(np.shape(Tsys)[1]):
    Tsys_norms[:,i] = normalize_array(Tsys[:,i], iants, obs_type, normScans=normScans)

## fit the linear relation between normalize Tsys and WVR
fit_results = dict.fromkeys([17,19,21,23])
for key in fit_results.keys():
    fit_results[key]= dict.fromkeys(['coeff','rel_err'])

for i in range(np.shape(Tsys)[1]):
    spw = int(17 + 2*i)
    xdata = WVR_norms; ydata = Tsys_norms[:,i]
    idx_nnan = ((~np.isnan(xdata)) & (~np.isnan(ydata)))
    results = np.polyfit(xdata[idx_nnan], ydata[idx_nnan], 1, full=True)
    fit_coeff = results[0]
    fit_err = results[1]
    fit_err_rel = np.sqrt(fit_err / len(ydata[idx_nnan])) / np.mean(ydata[idx_nnan])
    fit_results[spw]['coeff'] = fit_coeff
    fit_results[spw]['rel_err'] = fit_err_rel

## add the basic information of the fit_results
fit_results['info'] = {}
fit_results['info']['WVR chan'] = WVR_chan
fit_results['info']['avg time'] = Tsys_table['info']['avg time']
fit_results['info']['norm scans'] = normScans

## output the file into a pickle file
with open(fitfile, 'wb') as handle:
    pickle.dump(fit_results, handle)
