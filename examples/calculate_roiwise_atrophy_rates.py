import nibabel as nib
import numpy as np
import pandas as pd
import os
from os.path import join, exists
from scipy.stats import linregress


df = pd.read_csv("vallecas_dataframe.csv")
cohort_dir = '/mnt/nasneuro_share/data/derivatives/CAT12_cross/PVallecas'
parent_dir = os.path.dirname(os.getcwd())


atlas_niigz = join(parent_dir, 'resources', 'atlas', 'Harvard_Oxford_cat12_1.5mm_LZ.nii.gz')
atlas_img = nib.load(atlas_niigz)
atlas_data = atlas_img.get_fdata().astype(np.int16) # Convert to integer type

# Find all unique ROI labels in the atlas, excluding the background (0)
roi_labels = np.unique(atlas_data)
roi_labels = roi_labels[roi_labels != 0]


all_subject_slopes = []

print("Calculating ROI-wise slopes for each subject...")

for subject_ in pd.unique(df['subj']):
    
    subj_str = f'{subject_:04d}'
    subj_df = df.loc[df['subj'] == subject_]
    subj_dir = join(cohort_dir, str(subj_str))

    # Data for this subject
    visit_data = []

    for index_, row_ in subj_df.iterrows():
        visit_ = "V" + row_['subj+vis'][-2:]
        time_ = row_['yrs_from_mribl']
        visit_img_path = join(subj_dir, visit_, 'mri', f'smwp1{subj_str}_T1_{visit_}.nii')
        
        if exists(visit_img_path):
            img_data = nib.load(visit_img_path).get_fdata()
            visit_data.append({'time': time_, 'data': img_data})

    if len(visit_data) < 2:
        
        print(f"  Skipping subject {subj_str} (found {len(visit_data)} images).")
        continue

    # Sort visits by time to ensure correct order
    visit_data.sort(key=lambda x: x['time'])
    times_array = np.array([v['time'] for v in visit_data])
    
    subject_slopes = {'subj': subject_}

    # Loop through each ROI label
    for roi in roi_labels:
        # Get the boolean mask for the current ROI
        roi_mask = (atlas_data == roi)
        
        # Extract the mean GM value within the ROI mask for each time point
        roi_vols = [np.mean(v['data'][roi_mask]) for v in visit_data]
        
        # Calculate the slope (rate of change) for this ROI's time-series
        slope, intercept, r_value, p_value, std_err = linregress(times_array, roi_vols)
        
        subject_slopes[f'roi_{int(roi)}_slope'] = slope

    all_subject_slopes.append(subject_slopes)
    
# --- Create and Save Final DataFrame ---
# Convert the list of dictionaries into a clean DataFrame
slopes_df = pd.DataFrame(all_subject_slopes)

# Merge with original dataframe to get group information
final_df = pd.merge(df[['subj', 'ptau_C2N_2cut']].drop_duplicates(), slopes_df, on='subj')

# Save the final results to a single CSV file
output_csv_path = join('roi_slopes_by_subject_Vallecas.csv')
final_df.to_csv(output_csv_path, index=False)


# --- Calculate and Print Average Slopes by Group ---
print("\n--- Average Slopes by Group ---")
# Group by the p-tau category and calculate the mean for each slope column
group_avg_slopes = final_df.groupby('ptau_C2N_2cut').mean()

# Drop the subject ID column as it's not meaningful here
group_avg_slopes = group_avg_slopes.drop('subj', axis=1, errors='ignore')

print(group_avg_slopes)

for group in ["Low", "Intermediate", "Elevated"]:
    
    group_df = final_df[final_df['ptau_C2N_2cut'] == group]
    
    avg_slopes_for_group = group_df.drop(columns=['subj', 'ptau_C2N_2cut']).mean()

    group_avg_slope_map = np.zeros_like(atlas_data, dtype=np.float32)

    for col_name, avg_slope in avg_slopes_for_group.items():

        roi_label = int(col_name.replace('roi_', '').replace('_slope', ''))

        group_avg_slope_map[atlas_data == roi_label] = avg_slope


    output_filename = join(cohort_dir, f'average_roi_slope_map_{group}_C2N.nii.gz')
    avg_slope_img = nib.Nifti1Image(group_avg_slope_map, atlas_img.affine)
    nib.save(avg_slope_img, output_filename)