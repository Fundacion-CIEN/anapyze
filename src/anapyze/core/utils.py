import nibabel as nib
import numpy as np
from scipy.ndimage import zoom
from scipy.stats import t
import xmltodict
import re
from scipy.fftpack import fftn, fftshift
import pwlf
import matplotlib.pyplot as plt

def check_input_image_shape(img_data):

    print(img_data.shape)
    if img_data.ndim == 4:
        img_data = img_data[:, :, :, 0]

    return img_data

def change_image_dtype(img, new_dtype):
    """
    Changes datatype for input image
    :param img: nib image
    :param output_filepath: path to output image
    :param new_dtype: new datatype for output image (np.uint8, np.uint16, np.uint32, np.int8, np.int16, np.int32, np.float16, np.float32,np.float64)
    """

    # Change the data type of the image data
    img_data = img.get_fdata()
    new_img_data = img_data.astype(new_dtype)

    # Create a new NIfTI or Analyze image with the changed data type
    if isinstance(img, nib.nifti1.Nifti1Image):
        new_img = nib.Nifti1Image(new_img_data, img.affine, header = img.header)
    elif isinstance(img, nib.analyze.AnalyzeImage):
        header = img.header.copy()
        header.set_data_dtype(new_dtype)
        new_img = nib.analyze.AnalyzeImage(new_img_data, img.affine, header)
    else:
        raise TypeError("Unsupported image type. Input must be Nifti of Analyze")

    return new_img

def resample_image_by_matrix_size(img, target_shape, interpolation = "quadratic"):
    """
    # Example usage
    input_image_file = '/path/to/input/image/file.nii.gz'
    output_resampled_image_file = '/path/to/output/resampled/image/file.nii.gz'
    target_shape = (128, 128, 64)
    interpolation_method = 'quadratic'  # Specify the desired interpolation method
    resample_image(input_image_file, output_resampled_image_file, target_shape, interpolation_method)

    Interpolation options: nearest, linear, cubic, quadratic
    """

    # Load NIfTI or Analyze image
    img_data = img.get_fdata()

    # Calculate zoom factors for each dimension
    zoom_factors = np.array(target_shape) / np.array(img_data.shape)

    # Determine the order of interpolation based on the given method
    interpolation_methods = {
        "nearest": 0,
        "linear": 1,
        "cubic": 3,
        "quadratic": 4,
        # Add more interpolation methods and their corresponding order values here
        }
    order = interpolation_methods.get(
            interpolation, 1
            )  # Default to linear if method not recognized

    # Resample the image data using scipy's zoom function
    resampled_img_data = zoom(img_data, zoom_factors, order = order)

    # Update the affine matrix to reflect the new voxel dimensions
    voxel_sizes = np.array(img.header.get_zooms()) * (
            np.array(img_data.shape) / target_shape
    )
    new_affine = img.affine.copy()
    np.fill_diagonal(new_affine, voxel_sizes)

    # Create a new NIfTI or Analyze image with the resampled data and updated affine
    if isinstance(img, nib.nifti1.Nifti1Image):
        resampled_img = nib.Nifti1Image(
                resampled_img_data, new_affine, header = img.header
                )
    elif isinstance(img, nib.analyze.AnalyzeImage):
        header = img.header.copy()
        header.set_data_shape(target_shape)
        resampled_img: nib.AnalyzeImage = nib.analyze.AnalyzeImage(
                resampled_img_data, new_affine, header
                )
    else:
        raise TypeError("Unsupported image type. Input must be Nifti of Analyze")

    return resampled_img

def resample_image_by_voxel_sizes(img, target_voxel_sizes, interpolation = "linear"):
    """
    # Example usage
    input_image_file = '/path/to/input/image/file.nii.gz'
    output_resampled_image_file = '/path/to/output/resampled/image/file.nii.gz'
    target_voxel_sizes = (2.0, 2.0, 2.0)  # Specify the desired voxel sizes
    interpolation_method = 'linear'  # Specify the desired interpolation method

    resample_image_with_voxel_sizes(input_image_file, output_resampled_image_file, target_voxel_sizes, interpolation_method)
    """

    # Load NIfTI or Analyze image
    img_data = img.get_fdata()

    # Calculate zoom factors based on target voxel sizes
    current_voxel_sizes = np.array(img.header.get_zooms())
    zoom_factors = current_voxel_sizes / target_voxel_sizes

    # Determine the order of interpolation based on the given method
    interpolation_methods = {
        "nearest": 0,
        "linear": 1,
        "cubic": 3,
        "quadratic": 4,
        # Add more interpolation methods and their corresponding order values here
        }
    order = interpolation_methods.get(
            interpolation, 1
            )  # Default to linear if method not recognized

    # Resample the image data using scipy's zoom function
    resampled_img_data = zoom(img_data, zoom_factors, order = order)

    # Update the affine matrix to reflect the new voxel sizes
    new_affine = img.affine.copy()
    np.fill_diagonal(new_affine, target_voxel_sizes)

    # Create a new NIfTI or Analyze image with the resampled data and updated affine
    if isinstance(img, nib.nifti1.Nifti1Image):
        resampled_img = nib.Nifti1Image(
                resampled_img_data, new_affine, header = img.header
                )
    elif isinstance(img, nib.analyze.AnalyzeImage):
        header = img.header.copy()
        resampled_img = nib.analyze.AnalyzeImage(
                resampled_img_data, new_affine, header
                )
    else:
        raise TypeError("Unsupported image type. Input must be Nifti of Analyze")

    return resampled_img

def remove_nan_negs(img):
    """
    Removes nan and neg values from image
    :param input_filepath: Input image filepath as Nifti or Analyze
    :param output_filepath: Output image filepath as Nifti or Analyze
    """

    # Load NIfTI or Analyze image
    img_data = img.get_fdata()

    # Replace NaN and negative values with zeros
    img_data[np.isnan(img_data) | (img_data < 0)] = 0

    # Create a new NIfTI or Analyze image with cleaned data
    if isinstance(img, nib.nifti1.Nifti1Image):
        cleaned_img = nib.Nifti1Image(img_data, img.affine, header = img.header)
    elif isinstance(img, nib.analyze.AnalyzeImage):
        header = img.header.copy()
        cleaned_img = nib.analyze.AnalyzeImage(img_data, img.affine, header)
    else:
        raise TypeError("Unsupported image type. Input must be Nifti of Analyze")

    return cleaned_img

def add_poisson_noise(img, intensity_scaling_factor: float = 1.0):
    """Adds poison noise to an image"""
    # Load NIfTI or Analyze image

    img_data = img.get_fdata()

    # Apply Poisson noise to the image
    noisy_img_data = np.random.poisson(img_data * intensity_scaling_factor)

    noisy_img = nib.Nifti1Image(noisy_img_data, img.affine, header = img.header)

    return noisy_img

def create_mean_std_imgs(images):
    """
    This function creates the mean and standard deviation images for a list of images,
    and saves them in nifti files.

    :param images: a list of strings (nifti files paths)
    :param output_mean: the name of the nifti file that will contain the mean image
    :param output_std: the name of the nifti file that will contain the standard deviation image
    """

    sample_nii = images[0]
    sample_data = sample_nii.get_fdata()

    mean_data = sample_data * 0
    std_data = sample_data * 0

    data = sample_data[:, :, :, np.newaxis]

    for i in range(1, len(images)):

        img_data = images[i].get_fdata()
        img_data = img_data[:, :, :, np.newaxis]
        data = np.append(data, img_data, axis = 3)

    for i in range(sample_data.shape[0]):
        for j in range(sample_data.shape[1]):
            for k in range(sample_data.shape[2]):
                values = data[i, j, k, :]
                mean_val = np.mean(values)
                std_val = np.std(values)
                mean_data[i, j, k] = mean_val
                std_data[i, j, k] = std_val

    mean_img = nib.Nifti1Image(mean_data, sample_nii.affine, header = sample_nii.header)
    std_img = nib.Nifti1Image(std_data, sample_nii.affine, header = sample_nii.header)

    return mean_img, std_img

def create_atlas_csv_from_normals_imgs(normals, atlas_df, atlas_img_):

    """This function creates a csv file with the mean and
    standard deviation of the ROI values for a list of
    images, based on an atlas csv and hdr file.

    :param normals: a list of strings (nifti files paths)
    :param output_csv: the name of the csv file that will contain the output data
    :param atlas_csv:the CSV file that contains the atlas information (ROI_NUM, ROI_NAME)
    :param atlas_hdr: the name of the hdr file that contains the atlas image
    """

    atlas_data = atlas_img_.get_fdata()

    for indx_, row_ in atlas_df.iterrows():
        roi_num = row_["ROI_NUM"]
        roi_name = row_["ROI_NAME"]
        index_ = np.where(atlas_data == roi_num)

        roi_values = []

        for img_ in normals:

            img_data = img_.get_fdata()
            value = np.mean(img_data[index_])
            roi_values.append(value)

        roi_mean = np.mean(roi_values)
        roi_std = np.std(roi_values)

        atlas_df.loc[indx_, "ROI_MEAN"] = roi_mean
        atlas_df.loc[indx_, "ROI_STD"] = roi_std

        print(f"{roi_name}: {roi_mean} +/- {roi_std}")

    return atlas_df

def transform_img_to_atlas_zscores(img_, atlas_df, atlas_img_):
    """This function transforms an image to atlas z-scores, based on an atlas csv and hdr file,
    and saves the output image in a nifti file.

    :param img_: the name of the nifti file that contains the image to be transformed
    :param out: the name of the nifti file that will contain the output image
    :param atlas_csv: CSV containing the atlas information (ROI_NUM, MEAN, STD)
    :param atlas_hdr: the name of the hdr file that contains the atlas image
    """

    atlas_data = atlas_img_.get_fdata()
    pat_data = img_.get_fdata()

    pat_atlas = np.zeros(atlas_data.shape)

    for indx, row in atlas_df.iterrows():

        roi_num = row["ROI_NUM"]
        roi_mean = row["ROI_MEAN"]
        roi_std = row["ROI_STD"]

        index_ = np.where(atlas_data == roi_num)
        value = np.mean(pat_data[index_])
        z_score = (value - roi_mean) / roi_std
        pat_atlas[index_] = z_score

    out_img = nib.Nifti1Image(pat_atlas, atlas_img_.affine, header = atlas_img_.header)

    return out_img

def estimate_fwhm_mizutani(nifti: str, bin_size: int = 5, n_segs: int = 2, orientation = "axial", plot = False):
    
    """
    This function estimates image xy resolution based on a previous method
    implemented by MIZUTANI ET AL. for microscopy imaging:

    https://onlinelibrary.wiley.com/doi/10.1111/jmi.12315

    The idea of expanding this method to PET imaging was proposed by Carbonell et al:
    https://n.neurology.org/content/94/15_Supplement/4301

    The FWHMs are estimated from multiple regression of the logarithm of the square norm of
    the image Fourier transform against the square distance from the origin in the Fourier
    domain(essentially from what is known as a Wilson plot).
    The lower frequencies in the Wilson plot are linearly fitted and the PSF is estimated from the slope.

    :param nifti: input nifti image

    :param bin_size:  In the original paper from Mizutani, the logarithm of the average squared norm in
    each  5 × 5 pixel bin of the Fourier transform was used. You can vary this to check what fits your data
    better. Values between 5 and 10 seem to work well for PET images.
    :param n_segs: the number of segments of the Fourier transform.
    :param orientation: plane to walk traverse the image (axial, sagittal, coronal).
    :param plot: If True, the function will plot the Wilson plots and fitted lines for quality check.
    :return: The average FWHM and sigma across all slices in the image.
    """

    img = nib.load(nifti)
    volume = img.get_fdata()
    
    image_xy_size = np.abs(img.affine[0, 0])
    fwhm_values = []
    sigma_values = []

    if orientation == "axial":
        orient = 2
    elif orientation == "coronal":
        orient = 1
    elif orientation == "sagittal":
        orient = 0
    else:
        raise ValueError("orientation must be set to axial, coronal or sagital")

    for i in range(volume.shape[orient]):
        if orientation == "axial":
            slice_2d = volume[:, :, i]
        elif orientation == "coronal":
            slice_2d = volume[:, i, :]
        elif orientation == "sagittal":
            slice_2d = volume[i, :, :]
        else:
            raise TypeError("orientation must be set to axial, coronal or sagital")

        # Compute the 2D Fourier transform of the input slice
        fourier_slice = fftshift(fftn(slice_2d))

        # Compute the square norm of the Fourier transform
        square_norm = np.abs(fourier_slice) ** 2

        # Calculate logarithm of the square norm
        log_square_norm = np.log(square_norm + np.finfo(float).eps)

        # Calculate k^2 values (distances from the origin in Fourier domain)
        k_values = np.array(
                np.meshgrid(
                        np.fft.fftshift(np.fft.fftfreq(slice_2d.shape[0])),
                        np.fft.fftshift(np.fft.fftfreq(slice_2d.shape[1])),
                        indexing = "ij",
                        )
                )
        k_squared = np.sum(k_values ** 2, axis = 0)

        # Calculate the number of bins along each axis
        num_bins_x = slice_2d.shape[0] // bin_size
        num_bins_y = slice_2d.shape[1] // bin_size

        # Initialize binned arrays for the logarithm of the average squared norm and k^2 values
        log_square_norm_binned = np.zeros((num_bins_x, num_bins_y))
        k_squared_binned = np.zeros((num_bins_x, num_bins_y))

        for x in range(num_bins_x):
            for y in range(num_bins_y):
                # Compute the average of log_square_norm and k_squared within the 5x5 bin
                log_square_norm_binned[x, y] = np.mean(
                        log_square_norm[
                        x * bin_size: (x + 1) * bin_size,
                        y * bin_size: (y + 1) * bin_size,
                        ]
                        )
                k_squared_binned[x, y] = np.mean(
                        k_squared[
                        x * bin_size: (x + 1) * bin_size,
                        y * bin_size: (y + 1) * bin_size,
                        ]
                        )

        # Flatten the binned arrays and remove zero elements
        k_squared_flat = k_squared_binned.flatten()
        log_square_norm_flat = log_square_norm_binned.flatten()

        non_zero_mask = k_squared_flat > 0
        k_squared_flat = k_squared_flat[non_zero_mask]
        log_square_norm_flat = log_square_norm_flat[non_zero_mask]

        # Instantiate the piecewise linear regression model
        model = pwlf.PiecewiseLinFit(k_squared_flat, log_square_norm_flat)

        # Determine the optimal number of line segments
        n_segments = n_segs
        model.fit(n_segments)

        # Predict the fitted line
        x_pred = np.linspace(k_squared_flat.min(), k_squared_flat.max(), 100)
        y_pred = model.predict(x_pred)

        # Extract the slope and intercept of the fitted line
        slope, intercept = model.slopes[0], model.intercepts[0]

        # Calculate the width σ of the standard PSF
        sigma = np.sqrt(-slope / (4 * np.pi ** 2))
        sigma_values.append(sigma)

        # Calculate the FWHM of the PSF
        fwhm = 2 * np.sqrt(2 * np.log(2)) * sigma * image_xy_size
        fwhm_values.append(fwhm)

        if i == volume.shape[2] // 3 and plot:
            # Plot the Wilson plot with the fitted line overlaid
            plt.scatter(k_squared_flat, log_square_norm_flat, s = 1)
            plt.plot(x_pred, y_pred, color = "black", linewidth = 1)
            plt.xlabel("|k|^2")
            plt.ylabel("ln|F(k)|^2")
            plt.title("Wilson plot with fitted line")
            plt.ylim(
                    [np.min(log_square_norm_flat) - 5, np.max(log_square_norm_flat) + 5]
                    )
            plt.show()

    return np.nanmean(fwhm_values), np.nanmean(sigma_values)

def spm_map_2_cohens_d(img_path: str, out_path: str, len_1: int, len_2: int):
    """
    Converts an image of t_values to cohens_d

    :param img: Input image (spmT_0001.nii)
    :param out: Output file name
    :param len_1: len of group 1 in stat comparison
    :param len_2: len of group 2 in stat comparison

    """
    img = nib.load(img_path)
    data = img.get_fdata()

    d_coeff = np.sqrt(1 / len_1 + 1 / len_2)
    data = data * d_coeff

    cohens_img = nib.Nifti1Image(data, img.affine, img.header)

    nib.save(cohens_img, out_path)

def get_fdr_thresholds_from_spmt(img_, n1: int, n2: int):
    """
    :param img_: Path to spmT_0001.nii
    :param n1: len of group 1 in stat comparison
    :param n2: len of group 2 in stat comparison
    :return: FDR-corrected Cohen's d threshold
    """
    # Load the NIFTI image
    img_in = nib.load(img_)
    data = img_in.get_fdata()

    # Flatten the data to get a 1D array of t-values
    t_values = data.flatten()
    t_values = abs(np.unique(t_values[t_values != 0]))
    t_values = np.sort(t_values)

    df = n1 + n2 - 2
    p_values = t.sf(abs(t_values), df=df)
    indx = np.where(p_values < 0.05)
    thresholded = t_values[indx]
    t_thres = np.percentile(thresholded, 5)

    d_coeff = np.sqrt(1 / n1 + 1 / n2)
    cohens_thres = t_thres * d_coeff

    return t_thres, cohens_thres

def get_tiv_from_cat12_xml_report(cat_xml_filepath: str):
    """parse the information from a list-like object of "cat_*.xml" filepaths to
    a list of dictionaries for more easy data handling"""

    with open(cat_xml_filepath) as file:
        cat_xml_dict = xmltodict.parse(file.read())

        try:
            vol_tiv = cat_xml_dict["S"]["subjectmeasures"]["vol_TIV"]
            return vol_tiv

        except KeyError:
            raise KeyError("Could not extract TIV")

def get_weighted_average_iqrs_from_cat12_xml_report(cat_xml_filepath: str):
    """Extract Weighted Average IQRS from dictionaries produced by _parse_xml_files_to_dict"""

    with open(cat_xml_filepath) as file:
        cat_xml_dict = xmltodict.parse(file.read())

    pattern = "(Image Quality Rating \(IQR\):) (\d\d.\d\d)% \(([A-Z](-|\+)?)\)"

    try:
        catlog = cat_xml_dict["S"]["catlog"]["item"]
        for e in catlog:
            if e.startswith("Image Quality Rating (IQR)"):
                match = re.search(pattern, e)
                weighted_average_iqr = match.group(2)
                weighted_average_iqr = float(weighted_average_iqr)
                return weighted_average_iqr

    except:
        raise KeyError("Could not extract IQRS")