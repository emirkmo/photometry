## Installation

### Setup virtual environment (optional, but recommended)
<pre><code>$ cd /directory/for/virtual/environments
$ python3 -m venv --copies seeing
$ source seeing/bin/activate</code></pre>

### Installing `seeing`
<pre><code>$ cd /directory/of/seeing
$ pip install -r requirements.txt
$ python setup.py install</code></pre>

### Example

<pre><code>$ seeing image.fits --header SEEING</code></pre>

Run `$ seeing --help` for a list of methods and arguments.
