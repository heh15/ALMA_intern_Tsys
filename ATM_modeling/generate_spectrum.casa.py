import time
import analysisUtils as aU
import numpy as np

###########################################################
# directories

Dir = '/home/heh15/intern/ATM_modeling/'
specDir = Dir+'spectrum/' 

###########################################################
# functions

def count_time(stop, start):
    '''
    Convert the time difference into human readable form. 
    '''
    dure=stop-start
    m,s=divmod(dure,60)
    h,m=divmod(m,60)
    print("%d:%02d:%02d" %(h, m, s))

    return


def generate_ATM_spectrum(frequency, pwv, elevation, outfile):
    '''
    Generate ATM modeled Tsys spectrum using aU.plotAtmosphere()
    function. 
    '''
    aU.plotAtmosphere(frequency=frequency, pwv=pwv, elevation=elevation,
                      temperature=274, h0=1, pressure=557, telescope='ALMA',
                      quantity='tsys', numchan=128, showplot=False,
                      outfile = outfile)

    return

def generate_Tsys_filename(DataLabel, spw, pwv, elevation):
    '''
    Generate the outfile name for the ATM modeling
    '''
    elevation_str = str(elevation)
    spw_str = str(spw)
    pwv_str = str(round(pwv,2))
    keywords_filename = 'spw'+spw_str+'_elevation'+elevation_str+'_pwv'+pwv_str
    outfile = specDir+'Tsys_'+DataLabel+'_'+keywords_filename+'.txt'
   
    return outfile 

def generate_Twvr_filename(chan, pwv, elevation):
    '''
    Generate TWVR spectrum. 
    '''
    elevation_str = str(elevation)
    chan_str = str(chan)
    pwv_str = str(round(pwv,2))
    keywords_filename = 'chan'+chan_str+'_elevation'+elevation_str+'_pwv'+pwv_str
    outfile = specDir+'Twvr_'+keywords_filename+'.txt'

    return outfile

def generate_freq_range(freq_center, spw_width):
    '''
    ------
    Parameters:
    freq_center: np.array
        Read from 'listobs' channel averaged spectral window (e.g. spw 18 for Tsys
        spw 17. 
    '''
    freq_low = freq_center - spw_width/2
    freq_high = freq_center + spw_width/2

    return freq_low, freq_high

###########################################################

start = time.time()

# # WVR data
# # chans = [0,1,2,3]
# chans = [0,1]
# elevations = np.arange(20, 80, 1)
# pwvs = np.arange(0.1, 1.1, 0.01)
# # generate frequency range
# frequencies_center = np.array([184.19,185.25,186.485,188.51])
# chan_width = np.array([0.16,0.75,1.25,2.5]) # in GHz
# frequencies_low = frequencies_center - chan_width/2
# frequencies_high = frequencies_center + chan_width/2
# for i, chan in enumerate(chans):
#     frequency = [frequencies_low[i], frequencies_high[i]]
#     for elevation in elevations:
#         for pwv in pwvs:
#             outfile = generate_Twvr_filename(chan, pwv, elevation)
#             generate_ATM_spectrum(frequency, pwv, elevation, outfile)

# Band8 data
DataLabel = 'Band8'
spws = [17, 19, 21, 23]
elevations = np.arange(40,75,1)
elevations = np.array([46, 53])
pwvs = np.arange(0.4, 1.2, 0.01)
# generate frequency range
frequencies_low = np.array([427.758096,429.570596,417.700471,419.575471])
spws = [17]
spw_width = 2
frequencies_high = frequencies_low + spw_width
# generate spectrum
for i, spw in enumerate(spws):
    frequency = [frequencies_low[i], frequencies_high[i]]
    for elevation in elevations:
        for pwv in pwvs:
            outfile = generate_Tsys_filename(DataLabel, spw, pwv, elevation)
            generate_ATM_spectrum(frequency, pwv, elevation, outfile) 


# # Band7a data
# DataLabel = 'Band7a'
# spws = [17]
# elevations = np.arange(30,65,1)
# elevations = np.arange(65,75,1) 
# pwvs = np.arange(0.3,0.8,0.01)
# # generate frequency range
# frequencies_center = np.array([331.187213])
# spw_width = 2
# frequencies_low, frequencies_high = generate_freq_range(frequencies_center, spw_width)
# # generate spectrum
# for i, spw in enumerate(spws):
#     frequency = [frequencies_low[i], frequencies_high[i]]
#     for elevation in elevations:
#         for pwv in pwvs:
#             outfile = generate_Tsys_filename(DataLabel, spw, pwv, elevation)
#             generate_ATM_spectrum(frequency, pwv, elevation, outfile)

# # Band9b1 data
# DataLabel = 'Band9b1'
# spws = [17]
# elevations = np.arange(30,45,1)
# elevations = np.arange(45,55,1) 
# pwvs = np.arange(0.1,0.7,0.01)
# # generate frequency range
# frequencies_center = np.array([657.028878])
# spw_width = 2
# frequencies_low, frequencies_high = generate_freq_range(frequencies_center, spw_width)
# # generate spectrum
# for i, spw in enumerate(spws):
#     frequency = [frequencies_low[i], frequencies_high[i]]
#     for elevation in elevations:
#         for pwv in pwvs:
#             outfile = generate_Tsys_filename(DataLabel, spw, pwv, elevation)
#             generate_ATM_spectrum(frequency, pwv, elevation, outfile)

# # Band7b1 data
# DataLabel = 'Band7b1'
# spws = [17]
# elevations = np.arange(50,70,1) 
# pwvs = np.arange(0.4,1.0,0.01)
# elevations = [60]
# pwvs = [0.5]
# # generate frequency range
# frequencies_center = np.array([321.338312])
# spw_width = 2
# frequencies_low, frequencies_high = generate_freq_range(frequencies_center, spw_width)
# # generate spectrum
# for i, spw in enumerate(spws):
#     frequency = [frequencies_low[i], frequencies_high[i]]
#     for elevation in elevations:
#         for pwv in pwvs:
#             outfile = generate_Tsys_filename(DataLabel, spw, pwv, elevation)
#             generate_ATM_spectrum(frequency, pwv, elevation, outfile)

 
stop = time.time()
count_time(stop, start)
