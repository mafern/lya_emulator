import sys

from make_paper_plots import *
from coarse_grid_plot import *

if __name__ == "__main__":
    sim_rootdir = sys.argv[1]
    savedir = sys.argv[2]

    testdir = sim_rootdir + '/Lya_Boss/hires_knots_test' #/share/hypatia/sbird
    emudir = sim_rootdir + '/Lya_Boss/hires_knots'
    #savedir = '/Users/kwame/Papers/emulator_paper_1/plots'

    #test_knot_plots(testdir=testdir, emudir=emudir, plotname="_Two_kf2", kf_bin_nums=[0,1]) #[33,34])
    plot_test_interpolate_kf_bin_loop(emudir, testdir, savedir=savedir, plotname="_Two_loop", kf_bin_nums=np.arange(2))