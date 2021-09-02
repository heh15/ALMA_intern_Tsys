import time
import copy

############################################################
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

############################################################
# basic parameters. 
parallel = False
parameters = {}

# import the parameters for the original data 
par_tclean = {}


par_tclean['vis'] = 'uid___A002_Xd80784_X26be.ms.split.cal'
par_tclean['imagename'] = 'J091840+023047_Band9_1st' 
par_tclean['phasecenter'] = 'J2000 09h18m40.927 02d30m45.9'
par_tclean['specmode'] = 'mfs'
par_tclean['spw'] = '17,19,21,23' 
par_tclean['imsize'] = [240, 240]
par_tclean['outframe'] = 'Bary' # default
par_tclean['cell'] = '0.07arcsec'
par_tclean['weighting'] = 'briggs' # default
par_tclean['robust'] = 0.0
par_tclean['deconvolver'] = 'hogbom' # default
par_tclean['gridder'] = 'mosaic'
par_tclean['niter'] = 10000
par_tclean['cyclefactor'] = 1.0 # default
par_tclean['pblimit'] = 0.2 # default
par_tclean['interactive'] = False  # default
par_tclean['threshold'] = 0.0
par_tclean['threshold_ratio'] = 2.0 # S/N cut ratio. 
par_tclean['usemask'] = 'auto-multithresh'

# parameters for original 1st observation of calibrated dataset
parameters['1st_v0'] = copy.deepcopy(par_tclean)

# parameters for original 2nd observation of calibrated dataset
parameters['2nd_v0'] = copy.deepcopy(par_tclean)
parameters['2nd_v0']['vis'] = 'uid___A002_Xd80784_X2dcf.ms.split.cal' 
parameters['2nd_v0']['imagename'] = 'J091840+023047_Band9_2nd'

# import the parameters for the calibrated data with modified Tsys
parameters['v1'] = copy.deepcopy(par_tclean)
parameters['v1']['vis'] = 'uid___A002_Xbe0d4d_X12f5_v1.asdm.sdm.ms.split.cal' 
parameters['v1']['imagename'] = 'arp220_band10_12m_v1'

# import the parameters for the calibrated data with modified Tsys
parameters['v2'] = copy.deepcopy(par_tclean)
parameters['v2']['vis'] = 'uid___A002_Xbe0d4d_X12f5_v2.asdm.sdm.ms.split.cal'
parameters['v2']['imagename'] = 'arp220_band10_12m_v2'

# import the parameters for the calibrated data with modified Tsys
parameters['v3'] = copy.deepcopy(par_tclean)
parameters['v3']['vis'] = 'uid___A002_Xbe0d4d_X12f5_v3.asdm.sdm.ms.split.cal'
parameters['v3']['imagename'] = 'arp220_band10_12m_v3'

# modified Tsys, with start Tsys, without gain cal. 
parameters['v4'] = copy.deepcopy(par_tclean)
parameters['v4']['vis'] = 'uid___A002_Xbe0d4d_X12f5_v4.asdm.sdm.ms.split.cal'
parameters['v4']['imagename'] = 'arp220_band10_12m_v4'

############################################################
# main program 

start = time.time()

# make dirty imgage 
key = '2nd_v0'
delmod(vis = parameters[key]['vis'])
tclean(vis = parameters[key]['vis'],
       imagename = parameters[key]['imagename'],
       phasecenter = parameters[key]['phasecenter'],
       specmode = parameters[key]['specmode'],
       spw = parameters[key]['spw'],
       outframe = parameters[key]['outframe'],
       cell = parameters[key]['cell'],
       imsize = parameters[key]['imsize'],
       weighting = parameters[key]['weighting'],
       robust = parameters[key]['robust'],
       deconvolver = parameters[key]['deconvolver'],
       gridder = parameters[key]['gridder'],
       niter = 0,
       cyclefactor = parameters[key]['cyclefactor'],
       pblimit = parameters[key]['pblimit'],
       interactive = parameters[key]['interactive'],
       parallel = parallel)


# # make dirty image for first half of scans
# key = 'v4'
# delmod(vis = parameters[key]['vis'])
# tclean(vis = parameters[key]['vis'],
#        imagename = parameters[key]['imagename']+'_1st',
#        phasecenter = parameters[key]['phasecenter'],
#        specmode = parameters[key]['specmode'],
#        spw = parameters[key]['spw'],
#        outframe = parameters[key]['outframe'],
#        cell = parameters[key]['cell'],
#        imsize = parameters[key]['imsize'],
#        weighting = parameters[key]['weighting'],
#        robust = parameters[key]['robust'],
#        deconvolver = parameters[key]['deconvolver'],
#        gridder = parameters[key]['gridder'],
#        niter = 0,
#        scan = '7,9,13,17', 
#        cyclefactor = parameters[key]['cyclefactor'],
#        pblimit = parameters[key]['pblimit'],
#        interactive = parameters[key]['interactive'],
#        parallel = parallel)
# 
# delmod(vis = parameters[key]['vis'])
# tclean(vis = parameters[key]['vis'],
#        imagename = parameters[key]['imagename']+'_2nd',
#        phasecenter = parameters[key]['phasecenter'],
#        specmode = parameters[key]['specmode'],
#        spw = parameters[key]['spw'],
#        outframe = parameters[key]['outframe'],
#        cell = parameters[key]['cell'],
#        imsize = parameters[key]['imsize'],
#        weighting = parameters[key]['weighting'],
#        robust = parameters[key]['robust'],
#        deconvolver = parameters[key]['deconvolver'],
#        gridder = parameters[key]['gridder'],
#        niter = 0,
#        scan = '21,25,29,33',
#        cyclefactor = parameters[key]['cyclefactor'],
#        pblimit = parameters[key]['pblimit'],
#        interactive = parameters[key]['interactive'],
#        parallel = parallel)


stop = time.time()
count_time(stop, start)
