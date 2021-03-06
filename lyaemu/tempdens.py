"""File to make a temperature density plot, weighted by HI fraction"""

import os.path
import numpy as np
from scipy.optimize import leastsq
import matplotlib
from fake_spectra import abstractsnapshot as absn
from fake_spectra import unitsystem as units
from fake_spectra.gas_properties import GasProperties
from fake_spectra.ratenetworkspectra import RateNetworkGas
matplotlib.use("PDF")
import matplotlib.pyplot as plt

def mean_density(hub, redshift, omegab=0.0465):
    """Get mean gas density at some redshift."""
    unit = units.UnitSystem()
    #in g cm^-3
    rhoc = unit.rho_crit(hub)

    #Convert to atoms per cm^-3
    rhoc /= unit.protonmass

    nH = rhoc * omegab * (1 + redshift)**3

    return nH

def fit_temp_dens_relation(logoverden, logT):
    """Fit a temperature density relation."""
    #ind = np.where((logoverden > -1.0) * (logoverden <  0.0) * (logT < 5.0))
    ind = np.where((logoverden <  1.0) * (logT < 5.0))

    logofor = logoverden[ind]
    logtfor = logT[ind]

    def min_func(param):
        """Function to minimize: power law fit to temperature density relation."""
        logT0 = param[0]
        gammam1 = param[1]
        #print(param)
        return logtfor - (logT0 + gammam1 * logofor)

    res = leastsq(min_func, np.array([np.log10(1e4), 0.5]), full_output=True)
    params = res[0]
    if res[-1] <= 0:
        print(res[3])
    return 10**params[0], params[1] + 1

def fit_td_rel_plot(num, base, nhi=True, nbins=500, gas="raw", plot=True):
    """Make a temperature density plot of neutral hydrogen or gas.
    Also fit a temperature-density relation for the total gas (not HI).
    Arguments:
        num - snapshot number
        base - snapshot base directory
        nbins - number of bins to use for the T-rho histogram
        gas - if "raw" use snapshot values for temperature and neutral fraction. Otherwise use rate network values.
        nhi - if True, plot neutral hydrogen, otherwise plot total gas density
        plot - if True, make a plot, otherwise just do the fit
    """
    snap = absn.AbstractSnapshotFactory(num, base)

    redshift = 1./snap.get_header_attr("Time") - 1
    hubble = snap.get_header_attr("HubbleParam")
    if gas == "raw":
        rates = GasProperties(redshift, snap, hubble)
    else:
        rates = RateNetworkGas(redshift, snap, hubble)

    dens = snap.get_data(0, "Density", -1)

    temp = rates.get_temp(0, -1)

    dens = rates.get_code_rhoH(0, -1)

    if nhi:
        nhi = rates.get_reproc_HI(0, -1)
    else:
        nhi = dens

    logdens = np.log10(dens)
    logT = np.log10(temp)
    mean_dens = mean_density(hubble, redshift, omegab=snap.get_omega_baryon())
    (T0, gamma) = fit_temp_dens_relation(logdens - np.log10(mean_dens), logT)
    print("z=%f T0(K) = %f, gamma = %g" % (redshift, T0, gamma))

    if plot:
        hist, dedges, tedges = np.histogram2d(logdens, logT, bins=nbins, weights=nhi, density=True)

        plt.imshow(hist.T, interpolation='nearest', origin='low', extent=[dedges[0], dedges[-1], tedges[0], tedges[-1]], cmap=plt.cm.cubehelix_r, vmax=0.75, vmin=0.01)

        plt.plot(np.log10(mean_dens), np.log10(T0), '*', markersize=10, color="gold")
        dd = np.array([-6,-5,-4,-3])
        plt.xticks(dd, [r"$10^{%d}$" % d for d in dd])
        tt = np.array([2000, 3000, 5000, 10000, 20000, 30000, 50000, 100000])
        plt.yticks(np.log10(tt), tt//1000)
        plt.ylabel(r"T ($10^3$ K)")
        plt.xlabel(r"$\rho$ (cm$^{-3}$)")

        plt.xlim(-6,-3)
        plt.ylim(3.4,5)
        plt.colorbar()
        plt.tight_layout()
    return T0, gamma

if __name__ == "__main__":
    (T0, gamma) = fit_td_rel_plot(10, os.path.expanduser("~/data/Lya_Boss/hires_s8_test/ns0.97As2.2e-09heat_slope0.083heat_amp0.92hub0.69/output/"), nhi=True)
    plt.savefig("plots/tempdens.pdf")
    plt.clf()
    (T0, gamma) = fit_td_rel_plot(7, os.path.expanduser("~/data/Lya_Boss/hires_s8_test/ns0.97As2.2e-09heat_slope0.083heat_amp0.92hub0.69/output/"), nhi=True)
    plt.savefig("plots/tempdens3.pdf")
    plt.clf()
