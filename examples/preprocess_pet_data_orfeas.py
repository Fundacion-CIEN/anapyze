import os
from os.path import join, exists
from anapyze.core import utils, processor
import nibabel as nib

dir_patients = r'/mnt/nasneuro_share/analysis/ovourkas/nifti_FDG_TauPET_Staging'
spm_path = r'/mnt/WORK/software/spm12'
smoothing = 6

#Parent directory of the current file
parent_dir = os.path.dirname(os.getcwd())

template_fdg_niigz = join(parent_dir, 'resources', 'templates', 'FDG_PET_template.nii.gz')
template_fdg_nii = template_fdg_niigz[:-7] + '.nii'

mask_niigz = join(parent_dir, 'resources', 'mask', 'gm_cat12.nii.gz')
mask_img = nib.load(mask_niigz)

# Open with nibabel and save as nii
template_fdg_img = nib.load(template_fdg_niigz)
nib.save(template_fdg_img, template_fdg_nii)

list_dirs = os.listdir(dir_patients)

# print("Spatial Normalization...")

# images_to_norm = []

# mfile_name = join(dir_patients, 'fdg_pet_spatial_norm.m')

# for i in list_dirs:

#     dir_subj = join(dir_patients, i)

#     fdg_image = join(dir_subj, f'{i}.nii')

#     if exists(fdg_image):

#         img_ = nib.load(fdg_image)
#         img_ = utils.remove_nan_negs(img_)

#         nib.save(img_, fdg_image)

#         images_to_norm.append(fdg_image)

#     else:
#         print('PET missing for directory: ', i)

# processor.old_normalize_spm(images_to_norm, template_fdg_nii, mfile_name, spm_path=spm_path)

print("Smoothing...")

images_to_smooth = []

mfile_name = join(dir_patients, 'fdg_pet_smooth.m')

for i in list_dirs:

    dir_subj = join(dir_patients, i)

    fdg_image = join(dir_subj, f'w{i}.nii')

    if exists(fdg_image):

        images_to_smooth.append(fdg_image)

processor.smooth_images_spm(images_to_smooth, [smoothing,smoothing,smoothing], mfile_name, spm_path=spm_path)

print("Intensity Normalization...")

for i in list_dirs:

    dir_subj = join(dir_patients, i)

    fdg_path = join(dir_subj, f'sw{i}.nii')

    if exists(fdg_path):
        fdg_img_ = nib.load(fdg_path)
        fdg_norm = join(dir_subj, 'swfdg_normhist.nii')

        norm_value, norm_image =  processor.intensity_normalize_pet_histogram(fdg_img_, template_fdg_img, mask_img)
        nib.save(norm_image, fdg_norm)

        print("Normalization_Value: ", norm_value)
