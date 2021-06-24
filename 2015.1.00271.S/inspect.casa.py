importasdm('uid___A002_Xbe0d4d_X12f5.asdm.sdm')

# check different spectral windows
listobs('uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms')
 

# plotms the bandpass for each antennae
plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='scan', spw='4', avgtime='1', plotfile='raw_WVR_all.png')

# plotms the SQLD for each antennae
spw = '0,1,2,3,13,14,15,16'
plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='scan', spw='0,1,2,3,13,14,15,16', avgtime='1', plotfile='raw_SQLD_all.png')

# plotms the chan_avg for each antennae
spw = '6,8,10,12,18,20,22,24'
plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='scan', spw=spw, avgtime='1', plotfile='raw_autocorrelation_all.png')


# iterate among different antennaes
for antennaid in range(46):
    antenna = str(antennaid) + '&&'
#     plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='scan', spw='4', avgtime='1', 
#            plotfile='raw_WVR_ant'+str(antennaid)+'.png',antenna=antenna)
    plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='scan', spw='0,1,2,3,13,14,15,16', avgtime='1', 
           plotfile='raw_SQLD_ant'+str(antennaid)+'.png',antenna=antenna)
    spw = '6,8,10,12,18,20,22,24'
    plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='scan', spw=spw, avgtime='1', 
           plotfile='raw_autocorrelation_ant'+str(antennaid)+'.png',antenna=antenna)

# check for spw 0, polarization XX for different antennaes
plotms(vis='uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms', xaxis='time', yaxis='amp', coloraxis='antenna1', spw='0', avgtime='1', correlation='XX', 
       plotfile='raw_SQLD_spw0_XX_all.png')
