__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.00740.S')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
context.set_state('ProjectStructure', 'ous_part_id', 'X2040714452')
context.set_state('ProjectStructure', 'ous_title', 'Undefined')
context.set_state('ProjectStructure', 'ppr_file', '/opt/dared/opt/dared.2018OCT/mnt/dataproc/2017.1.00740.S_2019_06_12T11_56_29.213/SOUS_uid___A001_X12d1_X2b8/GOUS_uid___A001_X12d1_X2bc/MOUS_uid___A001_X12d1_X2bd/working/PPR_uid___A001_X12d1_X2be.xml')
context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1221/X83d')
context.set_state('ProjectStructure', 'recipe_name', 'hifa_image')
context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1221/X839')
context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X12d1/X2bd')
try:
    hifa_restoredata(vis=['/opt/dared/opt/dared.2018OCT/mnt/dataproc/2017.1.00740.S_2019_06_12T11_56_29.213/SOUS_uid___A001_X12d1_X2b8/GOUS_uid___A001_X12d1_X2bc/MOUS_uid___A001_X12d1_X2bd/rawdata/uid___A002_Xd80784_X26be', '/opt/dared/opt/dared.2018OCT/mnt/dataproc/2017.1.00740.S_2019_06_12T11_56_29.213/SOUS_uid___A001_X12d1_X2b8/GOUS_uid___A001_X12d1_X2bc/MOUS_uid___A001_X12d1_X2bd/rawdata/uid___A002_Xd80784_X2dcf'], session=['session_1', 'session_2'], copytoraw=False)
    hif_mstransform(pipelinemode="automatic")
    hifa_flagtargets(pipelinemode="automatic")
    hifa_imageprecheck(pipelinemode="automatic")
    hif_checkproductsize(maxproductsize=400.0, maxcubesize=60.0, maxcubelimit=80.0)
    hif_makeimlist(specmode='mfs')
    hif_findcont(pipelinemode="automatic")
    hif_uvcontfit(pipelinemode="automatic")
    hif_uvcontsub(pipelinemode="automatic")
    hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(specmode='cont')
    hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(specmode='cube')
    hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(specmode='repBW')
    hif_makeimages(pipelinemode="automatic")
finally:
    h_save()
