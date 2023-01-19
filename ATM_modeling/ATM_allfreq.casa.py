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


def generate_ATM_spectrum(frequency, pwv, elevation, outfile, **kwargs):
    '''
    Generate ATM modeled Tsys spectrum using aU.plotAtmosphere()
    function. 
    '''
    aU.plotAtmosphere(frequency=frequency, pwv=pwv, elevation=elevation,
                      temperature=274, h0=1, pressure=557, telescope='ALMA',
                      quantity='tsys', showplot=False,
                      outfile = outfile, **kwargs)

    return

###########################################################
# main program

start = time.time()

Bands = np.array(['Band7','Band8','Band9','Band10'])

frequencies_low = np.array([273, 375, 600, 750])
frequencies_high = np.array([375, 500, 750, 1000])
chan_width = 0.016
num_chans = ((frequencies_high - frequencies_low) / chan_width).astype(int)

elevation = 50 
pwvs = np.arange(0.1, 1.1, 0.01)

Bands = Bands[3:]
num_chans = num_chans[3:]
frequencies_low = frequencies_low[3:]; frequencies_high = frequencies_high[3:]

for i, Band in enumerate(Bands):
    frequency_low = frequencies_low[i]; frequency_high = frequencies_high[i]
    frequency = [frequency_low, frequency_high]
    for pwv in pwvs:
        outfile = specDir + 'ATM_'+Band+'_elevation50_pwv'+str(round(pwv,2))+'.txt'
        generate_ATM_spectrum(frequency, pwv, elevation, outfile, numchan=num_chans[i])

stop = time.time()
count_time(stop, start)
