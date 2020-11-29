import re, glob, argparse, logging
from os.path import isabs, isfile, abspath
from itertools import count

import numpy as np

from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats

from photutils import IRAFStarFinder

def iraf_star_finder(data, guess, threshold):

    bg = type('background', (object,), dict(zip(
        ('mean', 'median', 'stddev'),
        sigma_clipped_stats(data[np.isfinite(data)])
    )))

    threshold = (5 * bg.stddev) if threshold is None else threshold

    if not guess is None:

        finder = IRAFStarFinder(threshold, guess)
        stars = finder(data - bg.median)

    else:

        guess = [2]

        while guess.count(guess[-1]) < 3:

            finder = IRAFStarFinder(threshold, guess[-1])
            stars = finder(data - bg.median)

            guess.append(np.round(stars['fwhm'].mean(), 3))

            if guess[-2] != guess[-1]: break

    return stars

def ravel_fits_files(files, directory='.'):

    filelist = []

    for f in files:

        if not isabs(f):
            f = abspath('%s/%s' % (directory, f))

        try:
            m = re.match('^(?:(.*)/)?(.+?)(?:\[(\d+)])?$', f)
            path, filename, hdu = m.groups()
        except:
            logging.error('couldn\'t parse %s', f)
            quit()
        else:
            path = ''  if path is None else path
            hdu  = hdu if hdu  is None else int(hdu)
            _hdu = 0   if hdu  is None else hdu

        if not isfile('%s/%s' % (path, filename)):
            
            _files = [_f + ('[%d]' % hdu if hdu else '')
                    for _f in glob.glob('%s/%s' % (path, filename))]

            if len(_files):
                filelist += ravel_fits_files(_files, path)
                continue
            else:
                logging.error('%s/%s doesn\'t exist', path, filename)
                quit()

        try:

            hdul = fits.open('%s/%s' % (path, filename))

        except OSError:

            with open(f, 'r') as fd:
                _files = fd.read().strip().split('\n')
            filelist += ravel_fits_files(_files, path)
            continue

        else:

            try:

                if len(hdul) <= _hdu or len(hdul[_hdu].data.shape) != 2 or not np.prod(hdul[_hdu].data.shape):

                    raise Exception('%s/%s[%d] doesn\'t exist or not compatible' % (path, filename, _hdu))

                elif not all(k in hdul[0 if hdu is None else hdu].header for k in ('crval1', 'crval2', 'crpix1', 'crpix2')):

                    raise Exception('%s/%s[%d] has no wcs' % (path, filename, _hdu))

            except Exception as e:

                logging.error(str(e))
                quit()

            finally:

                hdul.close()

            filelist.append(('%s/%s' % (path, filename), hdu))

    return filelist

def main():

    parser = argparse.ArgumentParser(description='Estimate seeing in FITS files.')
    parser.add_argument('fits', metavar='FITS', nargs='+', help='fits files or list of files')
    parser.add_argument('--header', metavar='KEYWORD', type=str, help='save seeing in header')
    parser.add_argument('--guess', metavar='SEEING', type=float, help='seeing guess in arcsec')
    parser.add_argument('--threshold', metavar='VALUE', type=float, help='absolute image value above which to select sources')
    args = parser.parse_args()

    files = ravel_fits_files(args.fits)

    seeings = dict()
    for f, hdu in files:

        _hdu = 0 if hdu is None else hdu

        with fits.open(f) as hdul:
            data = hdul[_hdu].data
            head = hdul[_hdu].header
            wcs = WCS(head)

        scale = np.sqrt(np.power(wcs.pixel_scale_matrix, 2).sum() / 2) # deg / pixel
        scale *= 60 * 60 # arcsec / pixel

        stars = iraf_star_finder(data, args.guess, args.threshold)
        fwhm = sigma_clipped_stats(stars['fwhm'])[0]

        seeings[f + ('' if hdu is None else ('[%d]' % hdu))] = fwhm * scale

    l0 = max(map(len, seeings.keys()))
    l1 = 4 + int(np.ceil(np.log10(max(seeings.values()))))
    for f, seeing in seeings.items():

        print(f.ljust(l0), ('%.3f' % seeing).rjust(l1))

    if args.header and input('Update header [Y/n] ').lower() in ('y', ''):

        for f, hdu in files:

            _hdu = 0 if hdu is None else hdu

            seeing = seeings[f + ('' if hdu is None else ('[%d]' % hdu))]

            with fits.open(f, mode='update') as hdul:
                hdul[_hdu].header.set(args.header, seeing, 'arcsec')
