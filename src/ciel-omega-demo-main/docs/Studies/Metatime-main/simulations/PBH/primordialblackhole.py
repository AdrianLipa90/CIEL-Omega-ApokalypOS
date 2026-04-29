"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats

# 1. Configuration & Target Selection
FITS_FILES = [
    '107_-26_Equ_J2000_planck_100Rel3.fits',
    '107_-26_Equ_J2000_planck_143Rel1.fits',
    '107_-26_Equ_J2000_planck_143Rel2.fits',
    '107_-26_Equ_J2000_planck_143Rel3.fits',
    '107_-26_Equ_J2000_planck_217Rel3.fits'
]

# Predicted PBH Coordinates
TARGET_COORD = SkyCoord(ra="07h10m18.395s", dec="-25d54m27.284s", frame='icrs')

def process_fits(file_path):
    print(f"\n--- Analyzing: {file_path} ---")
    with fits.open(file_path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
        wcs = WCS(header)

        # Handle NaNs in data
        data = np.nan_to_num(data, nan=np.nanmedian(data))

        # Convert World Coordinates to Pixel
        target_x, target_y = wcs.all_world2pix(TARGET_COORD.ra.deg, TARGET_COORD.dec.deg, 1)

        # 2. Background Subtraction & Statistics
        mean, median, std = sigma_clipped_stats(data, sigma=3.0)
        data_subtracted = data - median

        # 3. Point Source Detection (Looking for PBH Signature)
        # We look for sources at 5-sigma level
        daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)
        sources = daofind(data_subtracted)

        # 4. Visualization
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(1, 1, 1, projection=wcs)
        
        # Display the CMB map
        im = ax.imshow(data_subtracted, cmap='RdYlBu_r', origin='lower', vmin=-3*std, vmax=3*std)
        plt.colorbar(im, label='$\Delta T$ / Intensity (Background Subtracted)')

        # Mark predicted PBH position
        ax.scatter(target_x, target_y, s=300, edgecolors='lime', facecolors='none', 
                   lw=2, label='Predicted PBH Location', marker='o')
        
        # Mark detected point sources
        if sources:
            ax.scatter(sources['xcentroid'], sources['ycentroid'], s=50, 
                       color='black', marker='+', alpha=0.5, label='Detected Sources')
            
            # Check for proximity to target
            distances = np.sqrt((sources['xcentroid'] - target_x)**2 + (sources['ycentroid'] - target_y)**2)
            if np.min(distances) < 5: # Within 5 pixels
                print("!!! ALERT: Significant point source detected at PBH location !!!")
            else:
                print("No significant point source found at the exact PBH coordinates.")

        ax.set_title(f"PBH Search: {file_path}")
        ax.legend()
        plt.show()

if __name__ == "__main__":
    for f in FITS_FILES:
        try:
            process_fits(f)
        except Exception as e:
            print(f"Error processing {f}: {e}")
