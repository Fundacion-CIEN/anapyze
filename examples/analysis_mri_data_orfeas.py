import pandas as pd
import nibabel as nib
import os, itertools, shutil
from os.path import join, exists
from anapyze.analysis import two_samples

csv = '/mnt/nasneuro_share/analysis/ovourkas/Modified_PET_MRI_Data_FinalVisualRead.xlsx'
dir_patients = '/mnt/nasneuro_share/analysis/ovourkas/nifti_MRI_TauPET_Staging'
list_patids = os.listdir(dir_patients)

stat_analysis_dir = '/mnt/nasneuro_share/analysis/ovourkas/Statistical_Analyses'

spm_path = '/mnt/WORK/software/spm12'

parent_dir = os.path.dirname(os.getcwd())

mask_niigz = join(parent_dir, 'resources', 'mask', 'gm_cat12.nii.gz')
mask_nii = join(parent_dir, 'resources', 'mask', 'gm_cat12.nii')
mask_img = nib.load(mask_niigz)
nib.save(mask_img, mask_nii)

atlas_niigz = join(parent_dir, 'resources', 'atlas', 'Harvard_Oxford_cat12_1.5mm_LZ.nii.gz')

df = pd.read_excel(csv)

def can_convert_to_int(x):
    try:
        int(x)
        return True
    except (ValueError, TypeError):
        return False

# Fixing missing path var

for index_, row_ in df.iterrows():

    rid = row_["Subject_ID"]
    for j in list_patids:
        rid_candidate = j.split("_")[2]
        if can_convert_to_int(rid_candidate):
            if int(rid) == int(rid_candidate):
                df.loc[index_, "FOLDER_NAME"] = j

df.to_csv("/mnt/nasneuro_share/analysis/ovourkas/tau_pet_classified_fixed_subjids.csv")

stages = [0,1,2,3]

# Voxel-wise comparisons MRI Histogram_norm using SPM

for pair in itertools.combinations(stages, 2):
    
    print(pair)

    output_dir = join(stat_analysis_dir,f'VBM_MRI_Stage{pair[0]}_Stage{pair[1]}')
    
    df_group_1 = df.loc[df["TauPET_Staging"]==pair[0]]
    df_group_2 = df.loc[df["TauPET_Staging"]==pair[1]]

    images_group_1 = []
    ages_group_1 = []
    tivs_group_1 = []

    for index_, row_ in df_group_1.iterrows():

        dir_name = row_["FOLDER_NAME"]
        age = row_['Age_MRI']
        tiv = row_['vol_TIV']

        mri_img = join(dir_patients,dir_name,'mri',f'smwp1{dir_name}.nii')

        if exists(mri_img):
            images_group_1.append(mri_img)
            ages_group_1.append(age)
            tivs_group_1.append(tiv)

    images_group_2 = []
    ages_group_2 = []
    tivs_group_2 = []

    for index_, row_ in df_group_2.iterrows():

        dir_name = row_["FOLDER_NAME"]
        age = row_['Age_MRI']
        tiv = row_['vol_TIV']

        mri_img = join(dir_patients,dir_name,'mri',f'smwp1{dir_name}.nii')

        if exists(mri_img):
            images_group_2.append(mri_img)
            ages_group_2.append(age)
            tivs_group_2.append(tiv)


    two_samples.run_2sample_ttest_spm(spm_path=spm_path,save_dir=output_dir,
                                      group1=images_group_1,group2=images_group_2,
                                      group1_ages=ages_group_1, group2_ages=ages_group_2,
                                      covar2_name='TIV',
                                      group1_covar2=tivs_group_1,group2_covar2=tivs_group_2,
                                      mask=mask_nii)

# ROI-wise comparisons MRI Histogram_norm using SPM

for pair in itertools.combinations(stages, 2):
    
    print(pair)

    output_dir = join(stat_analysis_dir,f'ROIBased_MRI_Stage{pair[0]}_Stage{pair[1]}')

    if not exists(output_dir):
        os.makedirs(output_dir)
    
    df_group_1 = df.loc[df["TauPET_Staging"]==pair[0]]
    df_group_2 = df.loc[df["TauPET_Staging"]==pair[1]]

    images_group_1 = []

    for index_, row_ in df_group_1.iterrows():

        dir_name = row_["FOLDER_NAME"]

        mri_img = join(dir_patients,dir_name,'mri',f'vol_norm_gm.nii.gz')

        if exists(mri_img):
            images_group_1.append(mri_img)

    images_group_2 = []
    ages_group_2 = []

    for index_, row_ in df_group_2.iterrows():

        dir_name = row_["FOLDER_NAME"]

        mri_img = join(dir_patients,dir_name,'mri',f'vol_norm_gm.nii.gz')

        if exists(mri_img):
            images_group_2.append(mri_img)


    two_samples.run_2sample_ttest_atlas(images_group_1, images_group_2, atlas_niigz, output_dir, operation = "sum")