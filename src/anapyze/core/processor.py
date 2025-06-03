import nibabel as nib
import numpy as np
import subprocess
import os
from os.path import join, exists
from concurrent.futures import ThreadPoolExecutor

from anapyze.io import spm
from anapyze.io import cat12


def run_matlab_command(mfile, matlab_cmd="/usr/local/MATLAB/R2025a/bin/matlab"):
    mfile_path, mfile_name = os.path.split(mfile)

    command = f"{matlab_cmd} -nosplash -sd {mfile_path} -batch {mfile_name[0:-2]}"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if len(result.stderr) == 0:
        print(f"Successfully executed {mfile_name}")
    else:
        print(result)
        raise Exception(result.stderr)

def intensity_normalize_pet_histogram(input_image, template, mask):
    """Normalizes an image using the mode of an intensity histogram.
    More info at: https://pubmed.ncbi.nlm.nih.gov/32771619/

    :param input_image: the path to the input image
    :param template: the path to the template image
    :param mask: the path to the mask image
    :param output: the path to the output image
    :return: the normalization value used to scale the input image
    """

    fdg_data = input_image.get_fdata()
    template_data = template.get_fdata()
    mask_data = mask.get_fdata()

    if len(mask.shape) == 4:
        mask_data = mask_data[:, :, :, 0]

    indx = np.where(mask_data == 1)
    mean_template = np.mean(template_data[indx])
    mean_fdg = np.mean(fdg_data[indx])

    fdg_data = fdg_data * (mean_template / mean_fdg)

    division = template_data[indx] / fdg_data[indx]
    values, bins = np.histogram(division, 200, range=(0.5, 2))
    amax = np.amax(values)
    indx = np.where(values == amax)
    norm_value = float(bins[indx][0])
    norm_data = fdg_data * norm_value

    norm_img = nib.Nifti1Image(norm_data, input_image.affine, input_image.header)

    return norm_value, norm_img

def intensity_normalize_pet_ref_region(input_image, ref_region_img, ref_region_val=1):
    """Normalizes an image using a reference region.
    :param input_image: the path to the input image
    :param ref_region_img: the path to the reference region image
    :param ref_region_val:
    :return: the normalization value used to scale the input image
    """
    ref_data = ref_region_img.get_fdata()

    if len(ref_data) == 4:
        ref_data = ref_data[:, :, :, 0]

    ref_vox = np.where(ref_data == ref_region_val)
    img_data = input_image.get_fdata()

    if len(img_data.shape) == 4:
        img_data = img_data[:, :, :, 0]

    ref_value = np.mean(img_data[ref_vox])
    normalized_data = img_data / ref_value

    normalized_img = nib.Nifti1Image(normalized_data, input_image.affine, input_image.header)

    return normalized_img, ref_value

def histogram_matching(reference_img, input_img):
    """Matches the histogram of an input image to a reference image.

    :param reference_nii: the path to the reference image
    :param input_nii: the path to the input image
    :param output_nii: the path to the output image
    :return: None
    """

    nt_data = reference_img.get_fdata()
    pt_data = input_img.get_fdata()

    # Stores the image data shape that will be used later
    old_shape = pt_data.shape

    # Converts the data arrays to single dimension and normalizes by the maximum
    nt_data_array = nt_data.ravel()
    pt_data_array = pt_data.ravel()

    # get the set of unique pixel values and their corresponding indices and counts
    s_values, bin_idx, s_counts = np.unique(
        pt_data_array, return_inverse=True, return_counts=True
    )
    t_values, t_counts = np.unique(nt_data_array, return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    # Reshapes the corresponding values to the indexes and reshapes the array to input
    final_image_data = interp_t_values[bin_idx].reshape(old_shape)

    final_image = nib.Nifti1Image(final_image_data, input_img.affine, input_img.header)

    return final_image

def logpow_histogram_matching(reference_img, input_img, alpha: int = 1, beta: int = 3):
    """Matches the histogram of an input image to a reference image using a log-power transformation.
    More info: https://doi.org/10.1117/1.JEI.23.6.063017

    :param reference_nii: the path to the reference image
    :param input_nii: the path to the input image
    :param output_nii: the path to the output image
    :param alpha: the additive constant for the log transformation, defaults to 1
    :param beta: the power exponent for the log transformation, defaults to 3
    """
    nt_data = reference_img.get_fdata()
    pt_data = input_img.get_fdata()

    # Stores the image data shape that will be used later
    old_shape = pt_data.shape

    # Converts the data arrays to single dimension and normalizes by the maximum
    nt_data_array = nt_data.ravel()
    pt_data_array = pt_data.ravel()

    # get the set of unique pixel values and their corresponding indices and counts
    s_values, bin_idx, s_counts = np.unique(pt_data_array, return_inverse=True, return_counts=True)
    t_values, t_counts = np.unique(nt_data_array, return_counts=True)

    s_counts = np.power(np.log10(s_counts + alpha), beta)
    t_counts = np.power(np.log10(t_counts + alpha), beta)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    # Reshapes the corresponding values to the indexes and reshapes the array to input
    final_image_data = interp_t_values[bin_idx].reshape(old_shape)
    # final_image_data[indx] = 0

    final_image = nib.Nifti1Image(final_image_data, input_img.affine, input_img.header)

    return final_image

def coregister_spm(reference_nii, input_nii, mfile_name, spm_path="/Users/jsilva/software/spm12"):
    """Performs coregistration between two images using SPM."""

    spm.generate_mfile_coregister(spm_path, mfile_name,
                                  reference_nii, input_nii)

    run_matlab_command(mfile_name)

def old_normalize_spm(images_to_norm, template_image, mfile_name, spm_path="/Users/jsilva/software/spm12"):

    spm.generate_mfile_old_normalize(spm_path, mfile_name, images_to_norm, template_image)

    run_matlab_command(mfile_name)

def new_normalize_spm(images_to_norm, mfile_name, template_image = False, spm_path = "/Users/jsilva/software/spm12"):

    if template_image == False:
        template_image = join(spm_path, 'tpm', 'TPM.nii')

    spm.generate_mfile_new_normalize(spm_path, mfile_name, template_image, images_to_norm)

    run_matlab_command(mfile_name)

def old_deformations(images_to_deform, base_image, def_matrix, interpolation, mfile_name, spm_path="/Users/jsilva/software/spm12"):

    spm.generate_mfile_old_deformations(spm_path, mfile_name, def_matrix, base_image, images_to_deform, interpolation)
    run_matlab_command(mfile_name)

def new_deformations(images_to_deform,def_matrix,interpolation,mfile_name, spm_path="/Users/jsilva/software/spm12"):

    spm.generate_mfile_new_deformations(spm_path, mfile_name, def_matrix, images_to_deform, interpolation)
    run_matlab_command(mfile_name)

def smooth_images_spm(images_to_smooth, smoothing, mfile_name, spm_path="/Users/jsilva/software/spm12"):

    spm.generate_mfile_smooth_imgs(spm_path, mfile_name, images_to_smooth, smoothing)
    run_matlab_command(mfile_name)

def cat12_segmentation_crossec(images_to_segment, mfile_name, template_tpm = False, template_volumes = False,
                               output_vox_size = 1.5, bounding_box = "cat12", surface_processing = 0,
                               spm_path="/Users/jsilva/software/spm12"):

    if not template_tpm:
        template_tpm = join(spm_path, 'tpm', 'TPM.nii')

    if not template_volumes:
        template_volumes = join(spm_path, 'toolbox', 'cat12', 'templates_MNI152NLin2009cAsym', 'Template_0_GS.nii')

    cat12.generate_mfile_cat12_segmentation_crossec(spm_path, mfile_name,images_to_segment,
                                                    template_tpm,template_volumes,
                                                    output_vox_size = output_vox_size, bounding_box = bounding_box,
                                                    surface_processing = surface_processing)

    run_matlab_command(mfile_name)

def cat12_segmentation_longit(images_to_segment, mfile_name, template_tpm = False, template_volumes = False,
                              output_vox_size = 1.5, bounding_box = "cat12", surface_processing = 0,
                              spm_path="/Users/jsilva/software/spm12"):

    if not template_tpm:
        template_tpm = join(spm_path, 'tpm', 'TPM.nii')

    if not template_volumes:
        template_volumes = join(spm_path, 'toolbox', 'cat12', 'templates_MNI152NLin2009cAsym', 'Template_0_GS.nii')

    cat12.generate_mfile_cat12_segmentation_longit(spm_path, mfile_name,images_to_segment,
                                                    template_tpm,template_volumes,
                                                    output_vox_size = output_vox_size, bounding_box = bounding_box,
                                                    surface_processing = surface_processing)

    run_matlab_command(mfile_name)

def recon_all_freesurfer(t1_nii, t2_nii=False):

    if "FREESURFER_HOME" in os.environ:
        pass
    else:
        raise Exception("FREESURFER_HOME environment variable not set")

    #directory containing the t1_nii file
    pat_dir = os.path.split(t1_nii)[0]

    if exists(t1_nii):
        os.system(f"recon-all -sd {pat_dir} -i {t1_nii} -s FS_out -all\n")
    if exists(t1_nii) and exists(t2_nii):
        # TODO : hippocampal subfields
        pass

def recon_all_freesurfer_whole_cohort(cohort_dir, pats: dict, n_parallel: int = 2) -> None:

    if "FREESURFER_HOME" in os.environ:
        pass
    else:
        raise Exception("FREESURFER_HOME environment variable not set")

    def process_patient(item: tuple):

        pat, t1_name, t2_name = item
        pat_dir = join(cohort_dir, pat)
        t1_nii = join(cohort_dir, pat, t1_name)
        t2_nii = join(cohort_dir, pat, t2_name)

        if exists(t1_nii):
            os.system(f"recon-all -sd {pat_dir} -i {t1_nii} -s FS_out -all\n")
        if exists(t1_nii) and exists(t2_nii):
            # TODO : hippocampal subfields
            pass

    with ThreadPoolExecutor(max_workers = n_parallel) as executor:
        executor.map(process_patient, pats.items())
        return None

    # TODO: Similar functions for SAMSEG and Synthseg

def synthstrip_skull_striping_freesurfer(img_to_strip: str, out_: str = False, includes_csf = True):

    if "FREESURFER_HOME" in os.environ:
        pass
    else:
        raise Exception("FREESURFER_HOME environment variable not set")

    if not out_:
        out_path, out_name = os.path.split(img_to_strip)
        out_: str = join(out_path, 'skull_strip_' + out_name)

    csf_flag = ''
    if not includes_csf:
        csf_flag = '--no-csf'

    if exists(img_to_strip):
        os.system(f"mri_synthstrip -i {img_to_strip} -o {out_} {csf_flag}")

    else:
        raise FileExistsError("Input image does not exist")