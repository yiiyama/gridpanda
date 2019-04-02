#!/usr/bin/env python

def entries_exclusion(entries):
    return '(isUndefined(GLIDEIN_Entry_Name) || !stringListMember(GLIDEIN_Entry_Name, "{0}", ","))'.format(','.join(entries))

def sites_exclusion(sites):
    return '(isUndefined(GLIDEIN_Site) || !stringListMember(GLIDEIN_Site, "{0}", ","))'.format(','.join(sites))

default_excluded_entries = [
    'CMS_T2_US_Nebraska_Red',
    'CMS_T2_US_Nebraska_Red_op',
    'CMS_T2_US_Nebraska_Red_gw1',
    'CMS_T2_US_Nebraska_Red_gw1_op',
    'CMS_T2_US_Nebraska_Red_gw2',
    'CMS_T2_US_Nebraska_Red_gw2_op',
    'CMS_T3_MX_Cinvestav_proton_work',
    'CMS_T3_US_Omaha_tusker',
    'CMSHTPC_T1_FR_CCIN2P3_cccreamceli01_multicore',
    'CMSHTPC_T1_FR_CCIN2P3_cccreamceli02_multicore',
    'CMSHTPC_T1_FR_CCIN2P3_cccreamceli03_multicore',
    'CMSHTPC_T1_FR_CCIN2P3_cccreamceli04_multicore',
    'CMSHTPC_T2_FR_CCIN2P3_cccreamceli01_multicore',
    'CMSHTPC_T2_FR_CCIN2P3_cccreamceli02_multicore',
    'CMSHTPC_T2_FR_CCIN2P3_cccreamceli03_multicore',
    'CMSHTPC_T2_IT_Rome_cream01',
    'CMSHTPC_T3_US_Omaha_tusker',
    'Engage_US_MWT2_iut2_condce',
    'Engage_US_MWT2_iut2_condce_mcore',
    'Engage_US_MWT2_osg_condce',
    'Engage_US_MWT2_osg_condce_mcore',
    'Engage_US_MWT2_uct2_condce',
    'Engage_US_MWT2_uct2_condce_mcore',
    'Glow_US_Syracuse_condor',
    'Glow_US_Syracuse_condor-ce01',
    'Gluex_US_NUMEP_grid1',
    'HCC_US_BNL_gk01',
    'HCC_US_BNL_gk02',
    'HCC_US_BU_atlas-net2',
    'HCC_US_BU_atlas-net2_long',
    'HCC_US_SWT2_gk01',
    'IceCube_US_Wisconsin_osg-ce',
    'OSG_US_Clemson-Palmetto_condce',
    'OSG_US_Clemson-Palmetto_condce_mcore',
    'OSG_US_FIU_HPCOSGCE',
    'OSG_US_Hyak_osg',
    'OSG_US_IIT_iitgrid_rhel6',
    'OSG_US_MWT2_mwt2_condce',
    'OSG_US_MWT2_mwt2_condce_mcore',
    'OSG_US_UConn_gluskap',
    'OSG_US_SMU_mfosgce'
]

default_excluded_sites = [
  'HOSTED_BOSCO_CE'
]

if __name__ == '__main__':
    from argparse import ArgumentParser
    import pprint
    
    argParser = ArgumentParser(description = 'Generate exclusion list.')
    argParser.add_argument('--add-entry', '-e', metavar = 'ENTRY', dest = 'additional_entries', nargs = '+', default = [], help = 'More entries to exclude.')
    argParser.add_argument('--add-site', '-s', metavar = 'SITE', dest = 'additional_sites', nargs = '+', default = [], help = 'More sites to exclude.')

    args = argParser.parse_args()

    print entries_exclusion(default_excluded_entries + args.additional_entries) + ' && ' + sites_exclusion(default_excluded_sites + args.additional_sites)
