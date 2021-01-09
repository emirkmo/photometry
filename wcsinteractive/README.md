## Installation

### Setup virtual environment (optional, but recommended)
<pre><code>$ cd /directory/for/virtual/environments
$ python3 -m venv --copies wcsinteractive
$ source wcsinteractive/bin/activate</code></pre>

### Installing `wcsinteractive`
<pre><code>$ cd /directory/of/wcsinteractive
$ pip install -r requirements.txt
$ python setup.py install</code></pre>

### Running `wcsinteractive`
<pre><code>$ wcsinteractive</code></pre>

Scale is in arcsec/pixel, Seeing is in arcsec and R.A., Dec. and Radius are in degrees.

Custom catalog coordinates should be,\
R.A. | Dec. | Magnitude | Proper motion R.A. | Proper motion Dec. \
where magnitude and the proper motions are optional.
