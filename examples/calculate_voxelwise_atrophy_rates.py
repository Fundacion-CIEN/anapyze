import nibabel as nib
import numpy as np
import pandas as pd
import os
from os.path import join, exists
from anapyze.core import utils, processor

df = pd.read_csv("vallecas_dataframe.csv")

cohort_dir = '/mnt/nasneuro_share/data/derivatives/CAT12_cross/PVallecas'

spm_path = '/mnt/WORK/software/spm12'

#Parent directory of the current file
parent_dir = os.path.dirname(os.getcwd())

mask_niigz = join(parent_dir, 'resources', 'mask', 'gm_cat12.nii.gz')
mask_img = nib.load(mask_niigz)
mask_data = mask_img.get_fdata()[:,:,:,0]

template_img_path = '/mnt/nasneuro_share/data/derivatives/CAT12_cross/PVallecas/0001/V01/mri/smwp10001_T1_V01.nii'
template_img = nib.load(template_img_path)
template_data = template_img.get_fdata()


print("Smoothing...")

images_to_smooth = []

smoothing = 10

mfile_name = join(cohort_dir, 'gm_smooth.m')

for root, dirs, i_files in os.walk(cohort_dir):

    for i_file in i_files:

        if i_file[0:4] == 'mwp1':

            i_file_path = join(root, i_file)

            images_to_smooth.append(i_file_path)

processor.smooth_images_spm(images_to_smooth, [smoothing,smoothing,smoothing], mfile_name, spm_path=spm_path)

print("Calculate slope image for each subject...")

for subject_ in pd.unique(df['subj']):

    subj_str = f'{subject_:04d}'

    subj_df = df.loc[df['subj'] == subject_]
    subj_dir = join(cohort_dir, str(subj_str))

    subj_imgs_ = []
    times_ = []
    
    for index_, row_ in subj_df.iterrows():

        visit_ = "V" + row_['subj+vis'][-2:]
        time_ = row_['yrs_from_mribl']

        visit_img_path = join(subj_dir,visit_, 'mri', f'smwp1{subj_str}_T1_{visit_}.nii')
        
        if exists(visit_img_path):
            visit_img_ = nib.load(visit_img_path)
            visit_img_data = visit_img_.get_fdata()

            subj_imgs_.append(visit_img_data)

            # Potential improvement calculate volume at each visit as a percentage of the first visit
            # This way the slope will be a %change/year

            
            times_.append(time_)

            
    if len(subj_imgs_)>2:
        
        print(subject_)

        subj_4d_data = np.stack(subj_imgs_, axis=0)
        times_array = np.array(times_)

        mask_indices = np.where(mask_data == 1)

        masked_voxel_timeseries = subj_4d_data[:, mask_indices[0], mask_indices[1], mask_indices[2]]

        fit_coeffs = np.polyfit(times_array, masked_voxel_timeseries, 1)

        slopes = fit_coeffs[0, :]

        subject_slope_map = np.zeros_like(mask_data, dtype=np.float32)

        subject_slope_map[mask_indices] = slopes

        output_filename = join(subj_dir, f'slope_map_{subject_}.nii.gz')
        slope_img = nib.Nifti1Image(subject_slope_map, template_img.affine)
        nib.save(slope_img, output_filename)


print("Calculate average slope by group...")

for group in ["Low", "Intermediate", "Elevated"]:

    df_group = df.loc[df["ptau_C2N_2cut"] == group]

    group_images_ = []
    
    for subject_ in pd.unique(df_group['subj']):

        subj_str = f'{subject_:04d}'

        subj_dir = join(cohort_dir, str(subj_str))

        slopes_image_path = join(subj_dir, f'slope_map_{subject_}.nii.gz')

        if exists(slopes_image_path):

            slopes_img_ = nib.load(slopes_image_path)
            slopes_data_ = slopes_img_.get_fdata()

            group_images_.append(slopes_data_)

    average_slope_map = np.mean(group_images_, axis=0)

    print(group," has ", len, " subjects")

    # 2. Define the output filename for the group average map
    output_filename = join(cohort_dir, f'average_slope_map_{group}_C2N.nii.gz')

    # 3. Create a new NIfTI image with the averaged data and reference affine
    avg_slope_img = nib.Nifti1Image(average_slope_map, template_img.affine)

    # 4. Save the new image to the results directory
    nib.save(avg_slope_img, output_filename)
    







