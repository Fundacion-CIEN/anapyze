from nilearn.plotting.cm import _cmap_d as nilearn_cmaps
from neuromaps.transforms import mni152_to_fslr
from neuromaps.datasets import fetch_fslr
from surfplot import Plot
from surfplot.utils import threshold

def plot_atlas_result_to_surf(img_):

    gii_lh, gii_rh = mni152_to_fslr(img_, fslr_density='32k', method='nearest')

    # threshold after projection to avoid interpolation artefacts
    data_lh = threshold(gii_lh.agg_data(), 3)
    data_rh = threshold(gii_rh.agg_data(), 3)

    # get surfaces + sulc maps
    surfaces = fetch_fslr()
    lh, rh = surfaces['inflated']
    sulc_lh, sulc_rh = surfaces['sulc']

    p = Plot(lh, rh)
    p.add_layer({'left': sulc_lh, 'right': sulc_rh}, cmap='binary_r', cbar=False)

    # cold_hot is a common diverging colormap for neuroimaging
    cmap = nilearn_cmaps['cold_hot']
    p.add_layer({'left': data_lh, 'right': data_rh}, cmap=cmap,
                color_range=(-11, 11))

    # make a nice vertical colorbar on the right side of the figure
    kws = dict(location='right', draw_border=False, aspect=10, shrink=.2,
               decimals=0, pad=0)
    fig = p.build(cbar_kws=kws)
    fig.axes[0].set_title('MSC05 Left > Right Hand', pad=-3)
    fig.show()