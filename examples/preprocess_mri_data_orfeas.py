import os
from os.path import join, exists
from anapyze.core import utils, processor
import nibabel as nib
import pandas as pd

dir_patients = r'/mnt/nasneuro_share/analysis/ovourkas/nifti_MRI_TauPET_Staging'
spm_path = r'/mnt/WORK/software/spm12'
smoothing = 10

csv = "/mnt/nasneuro_share/analysis/ovourkas/tau_pet_classified_fixed_subjids.csv"
df = pd.read_csv(csv)

#Parent directory of the current file
parent_dir = os.path.dirname(os.getcwd())


list_dirs = os.listdir(dir_patients)

print("Smoothing...")

images_to_smooth = []

mfile_name = join(dir_patients, 'mri_gm_smooth.m')

for i in list_dirs:

    tiv = False

    dir_subj = join(dir_patients, i)

    mri_image = join(dir_subj, 'mri',f'mwp1{i}.nii')

    df_subj = df.loc[df["FOLDER_NAME"]==i]
    
    if not df_subj.empty:
        tiv = df_subj["vol_TIV"].values[0]

    if exists(mri_image) and tiv:

        images_to_smooth.append(mri_image)
        
        norm_image_out= join(dir_subj, 'mri',f'vol_norm_gm.nii.gz')

        img_ = nib.load(mri_image)
        data_ = img_.get_fdata()/tiv
        img_norm = nib.Nifti1Image(data_,img_.affine, img_.header)
        nib.save(img_norm,norm_image_out)


processor.smooth_images_spm(images_to_smooth, [smoothing,smoothing,smoothing], mfile_name, spm_path=spm_path)