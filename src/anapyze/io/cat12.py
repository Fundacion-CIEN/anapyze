import os
from os.path import join, exists
import shutil

def generate_mfile_cat12_segmentation_crossec(spm_path: str, mfile_name: str,
                                              images_to_seg: list,
                                              template_tpm: str,
                                              template_volumes: str,
                                              number_of_cores: int = 0,
                                              output_vox_size: float = 1.5,
                                              bounding_box: str = "cat12",
                                              surface_processing: int = 0):
    if type(images_to_seg) is str:
        # Do something
        images_to_norm = [images_to_seg]

    new_spm = open(mfile_name, "w")

    new_spm.write(f"addpath('{spm_path}')\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite."

    new_spm.write(design_type + "data = {\n")
    for i in range(len(images_to_seg)):
        new_spm.write("'" + images_to_seg[i] + ",1'\n")
    new_spm.write("};" + "\n")

    new_spm.write(design_type + "data_wmh = {''};" + "\n")
    new_spm.write(design_type + "nproc = " + str(number_of_cores) + ";\n")
    new_spm.write(design_type + "useprior = '';" + "\n")
    new_spm.write(design_type + "opts.tpm = {'" + template_tpm + "'};\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.opts."

    new_spm.write(design_type + "affreg = 'mni';" + "\n")
    new_spm.write(design_type + "biasacc = " + "0.5" + ";\n")
    new_spm.write(design_type + "accstr = " + "0.5" + ";\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.extopts.segmentation."

    new_spm.write(design_type + "restypes.optimal = " + "[1 0.3]" + ";\n")
    new_spm.write(design_type + "setCOM = " + "1" + ";\n")
    new_spm.write(design_type + "APP = " + "1070" + ";\n")
    new_spm.write(design_type + "affmod = " + "0" + ";\n")
    new_spm.write(design_type + "NCstr = " + "-Inf" + ";\n")
    new_spm.write(design_type + "spm_kamap = " + "0" + ";\n")
    new_spm.write(design_type + "LASstr = " + "0.5" + ";\n")
    new_spm.write(design_type + "LASmyostr = " + "0" + ";\n")
    new_spm.write(design_type + "gcutstr = " + "2" + ";\n")
    new_spm.write(design_type + "cleanupstr = " + "0.5" + ";\n")
    new_spm.write(design_type + "BVCstr = " + "0.5" + ";\n")
    new_spm.write(design_type + "WMHC = " + "2" + ";\n")
    new_spm.write(design_type + "SLC = " + "0" + ";\n")
    new_spm.write(design_type + "mrf = " + "1" + ";\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.extopts.registration."

    new_spm.write(
            design_type
            + "regmethod.shooting.shootingtpm = {'"
            + template_volumes
            + "'};\n"
            )
    new_spm.write(design_type + "regmethod.shooting.regstr = " + "0.5" + ";\n")
    new_spm.write(design_type + "vox = " + str(output_vox_size) + ";\n")

    if bounding_box == "cat12":
        new_spm.write(design_type + "bb = " + "12" + ";\n")
    elif bounding_box == "spm":
        new_spm.write(design_type + "bb = " + "16" + ";\n")
    else:
        raise ValueError("Bounding Box must be set to spm or cat12")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.extopts.surface."

    new_spm.write(design_type + "pbtres = " + "0.5" + ";\n")
    new_spm.write(design_type + "pbtmethod = " + "'pbt2x'" + ";\n")
    new_spm.write(design_type + "SRP = " + "22" + ";\n")
    new_spm.write(design_type + "reduce_mesh = " + "1" + ";\n")
    new_spm.write(design_type + "vdist = " + "2" + ";\n")
    new_spm.write(design_type + "scale_cortex = " + "0.7" + ";\n")
    new_spm.write(design_type + "add_parahipp = " + "0.1" + ";\n")
    new_spm.write(design_type + "close_parahipp = " + "1" + ";\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.extopts.admin."

    new_spm.write(design_type + "experimental = " + "0" + ";\n")
    new_spm.write(design_type + "new_release = " + "0" + ";\n")
    new_spm.write(design_type + "lazy = " + "0" + ";\n")
    new_spm.write(design_type + "ignoreErrors = " + "1" + ";\n")
    new_spm.write(design_type + "verb = " + "2" + ";\n")
    new_spm.write(design_type + "print = " + "2" + ";\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.output."

    new_spm.write(design_type + "BIDS.BIDSno = " + "1" + ";\n")
    new_spm.write(design_type + "surface = " + str(surface_processing) + ";\n")
    new_spm.write(
            design_type + "surf_measures = " + str(surface_processing) + ";\n"
            )

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.output.ROImenu.atlases."

    new_spm.write(design_type + "neuromorphometrics = " + "0" + ";\n")
    new_spm.write(design_type + "lpba40 = 0;\n")
    new_spm.write(design_type + "cobra = 0;\n")
    new_spm.write(design_type + "hammers = 0;\n")
    new_spm.write(design_type + "thalamus = 0;\n")
    new_spm.write(design_type + "thalamic_nuclei = 0;\n")
    new_spm.write(design_type + "suit = 0;\n")
    new_spm.write(design_type + "ibsr = 0;\n")
    new_spm.write(design_type + "aal3 = 0;\n")
    new_spm.write(design_type + "mori = 0;\n")
    new_spm.write(design_type + "anatomy3 = 0;\n")
    new_spm.write(design_type + "julichbrain = 0;\n")
    new_spm.write(design_type + "Schaefer2018_100Parcels_17Networks_order = 0;\n")
    new_spm.write(design_type + "Schaefer2018_200Parcels_17Networks_order = 0;\n")
    new_spm.write(design_type + "Schaefer2018_400Parcels_17Networks_order = 0;\n")
    new_spm.write(design_type + "Schaefer2018_600Parcels_17Networks_order = 0;\n")
    new_spm.write(design_type + "ownatlas = " + "{''}" + ";\n")

    design_type = "matlabbatch{1}.spm.tools.cat.estwrite.output."

    new_spm.write(design_type + "GM.native = 0;\n")
    new_spm.write(design_type + "GM.warped = 0;\n")
    new_spm.write(design_type + "GM.mod = 1;\n")
    new_spm.write(design_type + "GM.dartel = 0;\n")

    new_spm.write(design_type + "WM.native = 0;\n")
    new_spm.write(design_type + "WM.warped = 0;\n")
    new_spm.write(design_type + "WM.mod = 1;\n")
    new_spm.write(design_type + "WM.dartel = 0;\n")

    new_spm.write(design_type + "CSF.native = 0;\n")
    new_spm.write(design_type + "CSF.warped = 0;\n")
    new_spm.write(design_type + "CSF.mod = 1;\n")
    new_spm.write(design_type + "CSF.dartel = 0;\n")

    new_spm.write(design_type + "ct.native = 0;\n")
    new_spm.write(design_type + "ct.warped = 0;\n")
    new_spm.write(design_type + "ct.dartel = 0;\n")

    new_spm.write(design_type + "pp.native = 0;\n")
    new_spm.write(design_type + "pp.warped = 0;\n")
    new_spm.write(design_type + "pp.dartel = 0;\n")

    new_spm.write(design_type + "WMH.native = 0;\n")
    new_spm.write(design_type + "WMH.warped = 0;\n")
    new_spm.write(design_type + "WMH.mod = 0;\n")
    new_spm.write(design_type + "WMH.dartel = 0;\n")

    new_spm.write(design_type + "SL.native = 0;\n")
    new_spm.write(design_type + "SL.warped = 0;\n")
    new_spm.write(design_type + "SL.mod = 0;\n")
    new_spm.write(design_type + "SL.dartel = 0;\n")

    new_spm.write(design_type + "TPMC.native = 0;\n")
    new_spm.write(design_type + "TPMC.warped = 0;\n")
    new_spm.write(design_type + "TPMC.mod = 0;\n")
    new_spm.write(design_type + "TPMC.dartel = 0;\n")

    new_spm.write(design_type + "atlas.native = 0;\n")
    new_spm.write(design_type + "label.native = 1;\n")
    new_spm.write(design_type + "label.warped = 0;\n")
    new_spm.write(design_type + "label.dartel = 0;\n")
    new_spm.write(design_type + "labelnative = 1;\n")

    new_spm.write(design_type + "bias.native = 0;\n")
    new_spm.write(design_type + "bias.warped = 1;\n")
    new_spm.write(design_type + "bias.dartel = 0;\n")

    new_spm.write(design_type + "las.native = 0;\n")
    new_spm.write(design_type + "las.warped = 1;\n")
    new_spm.write(design_type + "las.dartel = 0;\n")

    new_spm.write(design_type + "jacobianwarped = 0;\n")
    new_spm.write(design_type + "warps = [1 0];\n")
    new_spm.write(design_type + "rmat = 0;\n")

    new_spm.close()


def generate_mfile_cat12_segmentation_longit(spm_path: str, mfile_name: str,
                                             images_to_seg: list,
                                             template_tpm: str,
                                             template_volumes: str,
                                             longmodel: int = 2,
                                             number_of_cores: int = 0,
                                             output_vox_size: float = 1.5,
                                             bounding_box: str = "cat12",
                                             surface_processing: int = 0,):

    # images_to_seg = [[subj1_image1, subj1_image2], [subj2_image1, subj2_image2]]

    new_spm = open(mfile_name, "w")

    new_spm.write(f"addpath('{spm_path}')\n")

    design_type = "matlabbatch{1}.spm.tools.cat.long."

    new_spm.write(design_type + "datalong.subjects = {\n")

    for i in range(len(images_to_seg)):
        new_spm.write("{\n")
        for j in range(len(images_to_seg[i])):
            new_spm.write("'" + images_to_seg[i][j] + "'\n")
        new_spm.write("}\n")
    new_spm.write("};\n")

    new_spm.write(design_type + "longmodel = " + str(longmodel) + ";\n")
    new_spm.write(design_type + "enablepriors = 1;\n")
    new_spm.write(design_type + "prepavg = 2;\n")
    new_spm.write(design_type + "bstr = 0;\n")
    new_spm.write(design_type + "avgLASWMHC = 0;\n")
    new_spm.write(design_type + "nproc = " + str(number_of_cores) + ";\n")
    new_spm.write(design_type + "opts.tpm = {'" + template_tpm + "'};\n")
    new_spm.write(design_type + "opts.affreg = 'mni';\n")
    new_spm.write(design_type + "opts.biasacc = 0.5;\n")

    design_type = "matlabbatch{1}.spm.tools.cat.long.extopts."

    new_spm.write(design_type + "restypes.optimal = [1 0.3];\n")
    new_spm.write(design_type + "setCOM = 1;\n")
    new_spm.write(design_type + "APP = 1070;\n")
    new_spm.write(design_type + "affmod = 0;\n")
    new_spm.write(design_type + "LASstr = 0.5;\n")
    new_spm.write(design_type + "LASmyostr = 0;\n")
    new_spm.write(design_type + "gcutstr = 2;\n")
    new_spm.write(design_type + "WMHC = 2;\n")
    new_spm.write(design_type + "registration.shooting.shootingtpm = {'" + template_volumes + "'};\n")
    new_spm.write(design_type + "registration.shooting.regstr = 0.5;\n")
    new_spm.write(design_type + "vox = " + str(output_vox_size) + ";\n")

    if bounding_box == "cat12":
        new_spm.write(design_type + "bb = 12;\n")
    elif bounding_box == "spm":
        new_spm.write(design_type + "bb = 16;\n")
    else:
        raise ValueError("Bounding Box must be set to spm or cat12")

    new_spm.write(design_type + "SRP = 22;\n")
    new_spm.write(design_type + "ignoreErrors = 1;\n")

    design_type = "matlabbatch{1}.spm.tools.cat.long."

    new_spm.write(design_type + "output.BIDS.BIDSno = 1;\n")
    new_spm.write(design_type + "output.surface = " + str(surface_processing) + ";\n")
    new_spm.write(design_type + "ROImenu.noROI = struct([]);\n")
    new_spm.write(design_type + "longTPM = 1;\n")
    new_spm.write(design_type + "modulate = 1;\n")
    new_spm.write(design_type + "dartel = 0;\n")
    new_spm.write(design_type + "printlong = 2;\n")
    new_spm.write(design_type + "delete_temp = 1;\n")

    new_spm.write("\n")
    new_spm.write("spm('defaults','fmri');\n")
    new_spm.write("spm_jobman('initcfg');\n")
    new_spm.write("spm_jobman('run',matlabbatch);\n")

    new_spm.close()


def generate_mfile_cat12_new_tiv_model(spm_path: str, mfile_name: str, save_dir: str,
                           group1: list, group1_ages: list, group1_tivs: list,
                           group2: list, group2_ages: list, group2_tivs: list,
                           mask: str,):

    if exists(save_dir):
        shutil.rmtree(save_dir)

    os.makedirs(save_dir)

    new_spm = open(mfile_name, "w")

    new_spm.write(f"addpath('{spm_path}')\n")

    design_type = "matlabbatch{1}.spm.tools.cat.factorial_design."

    new_spm.write(
            design_type + "dir = {'" + save_dir + "/'};\n"
            + design_type + "des.t2.scans1 = {\n"
            )

    for image in group1:
        new_spm.write("'" + image + ",1'\n")
    new_spm.write("};\n")

    new_spm.write(design_type + "des.t2.scans2 = {\n")

    for image in group2:
        new_spm.write("'" + image + ",1'\n")
    new_spm.write("};\n")

    new_spm.write(
            design_type + "des.t2.dept = 0;\n"
            + design_type + "des.t2.variance = 1;\n"
            + design_type + "des.t2.gmsca = 0;\n"
            + design_type + "des.t2.ancova = 0;\n"
            )

    new_spm.write(design_type + "cov.c = [")
    for age in group1_ages:
        new_spm.write(str(age) + "\n")
    for age in group2_ages:
        new_spm.write(str(age) + "\n")
    new_spm.write("];\n")

    new_spm.write(
            design_type + "cov.cname = 'Age';\n"
            + design_type + "cov.iCFI = 1;\n"
            + design_type + "cov.iCC = 5;\n"
            )

    new_spm.write(
            design_type + "multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});\n"
            )

    new_spm.write(
            design_type + "masking.tm.tm_none = 1;\n"
            + design_type + "masking.im = 1;\n"
            )

    new_spm.write(design_type + "masking.em = {'" + mask + "'}\n;")

    new_spm.write(design_type + "globals.g_ancova.global_uval = [")
    for tiv in group1_tivs:
        new_spm.write(str(tiv) + "\n")
    for tiv in group2_tivs:
        new_spm.write(str(tiv) + "\n")
    new_spm.write("];\n")

    new_spm.write(
            design_type + "check_SPM.check_SPM_zscore.do_check_zscore.use_unsmoothed_data = 1;\n"
            + design_type + "check_SPM_zscore.do_check_zscore.adjust_data = 1;\n"
            + design_type + "check_SPM.check_SPM_ortho = 1;\n"
            )

    spm_mat = join(save_dir, "SPM.mat")
    design_type = "matlabbatch{2}.spm.stats.fmri_est."

    new_spm.write(design_type + "spmmat = {'" + spm_mat + "'};\n")
    new_spm.write(design_type + "write_residuals = 0;")
    new_spm.write(design_type + "method.Classical = 1;")

    design_type = "matlabbatch{3}.spm.stats.con."
    contrast_name = "Atrophy"
    contrast = "[1 -1 0 0]"

    new_spm.write(design_type + "spmmat = {'" + spm_mat + "'};\n")
    new_spm.write(design_type + "consess{1}.tcon.name = '" + contrast_name + "';\n")
    new_spm.write(design_type + "consess{1}.tcon.weights =" + contrast + ";\n")
    new_spm.write(design_type + "consess{1}.tcon.sessrep = 'none';\n")
    new_spm.write(design_type + "delete = 0;\n")

    new_spm.close()
