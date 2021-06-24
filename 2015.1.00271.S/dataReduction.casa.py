import analysisUtils as aU
es = aU.stuffForScienceDataReduction()

###########################################################
# basic parameters 

asdm = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm'
vis = 'uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms'

###########################################################
# main program

# importasdm
rmtables('uid___A002_Xbe0d4d_X12f5.asdm.sdm.ms')
importasdm('uid___A002_Xbe0d4d_X12f5.asdm.sdm', asis='*')

## generate the calibration script
# es.generateReducScript(vis)

## inspect the .tsys table
tb.open('uid___A002_Xe48598_X7857.ms.tsys')
tb0 = tb.copy('uid___A002_Xe48598_X7857.ms.tsys')
tb.close()
columns = tb0.colnames()
Tsys_time = tb0.getcol('TIME')
Tsys_interval = tb0.getcol('INTERVAL')
Tsys_spectrum = tb0.getcol('FPARAM')

## check the Tsys table in the raw dataset
tb.open(vis+'SYSCAL')
tb1 = tb.copy(vis+'SYSCAL')
tb.close()
columns1 = tb1.colnames()
Tsys_spectrum1 = tb1.getcol('TSYS_SPECTRUM')
Tsys_time1 = tb1.getcol('TIME')
Tsys_interval1 = tb1.getcol('INTERVAL')

## check the WVR correction
tb.open('uid___A002_Xe48598_X7857.ms.wvr')
tb2 = tb.copy('uid___A002_Xe48598_X7857.ms.wvr')
tb.close()
columns2 = tb2.colnames()
wvr_spws = tb2.getcol('SPECTRAL_WINDOW_ID') # spws 17,25,27,29

wvr_rows = tb2.selectrows([0, 92496]) 
for name in columns2:
    print(wvr_rows.getcol(name)

## check the applycal command
from recipes.almahelpers import tsysspwmap
tsysmap = tsysspwmap(vis = 'uid___A002_Xe48598_X7857.ms', tsystable = 'uid___A002_Xe48598_X7857.ms.tsys', tsysChanTol = 1) 

'''
summary 
1. The generated .tsys table has the same length in time as the 
original SYSCAL table
2. The 'FPARAM' column is where Tsys spectrum stored in .tsys 
table
3. The 'PARAMERR' should be the parameter error, which is constantly
0.1. 
4. The 'ANTENA2' column is constant -1 in the .tsys table. 
5. Apply tsysmap to the newly created table. The value for different spws for the newly created table should be the same. 
'''

## write the modified Tsys table
# import the normalized WVR data


tb.create(tablename='uid___A002_Xe48598_X7857.extrap.tsys')
 
