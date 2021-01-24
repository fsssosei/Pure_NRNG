# Pure_NRNG

![PyPI](https://img.shields.io/pypi/v/pure_nrng?color=red)
![PyPI - Status](https://img.shields.io/pypi/status/pure_nrng)
![GitHub Release Date](https://img.shields.io/github/release-date/fsssosei/pure_NRNG)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/fsssosei/Pure_NRNG.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/fsssosei/Pure_NRNG/context:python)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bf34f8d12be84b4492a5a3709df0aae5)](https://www.codacy.com/manual/fsssosei/pure_nrng?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=fsssosei/pure_nrng&amp;utm_campaign=Badge_Grade)
![PyPI - Downloads](https://img.shields.io/pypi/dw/pure_nrng?label=PyPI%20-%20Downloads)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pure_nrng)
![PyPI - License](https://img.shields.io/pypi/l/pure_nrng)

*Generate multi-precision non-deterministic random Numbers package in python.*

According to the calculation of the minimum entropy value of the raw entropy, the adaptive absorption of the appropriate entropy bit.

## Installation

Installation can be done through pip. You must have python version >= 3.8

	pip install pure-nrng

## Usage

The statement to import the package:

	from pure_nrng_package import pure_nrng
	or
	from pure_nrng_package import *

Example:

	>>> nrng_instance = pure_nrng()
	>>> true_rand_bits = nrng_instance.true_rand_bits(256)
	>>> next(true_rand_bits)
	>>> true_rand_float = nrng_instance.true_rand_float(256)
	>>> next(true_rand_float)
	>>> true_rand_int = nrng_instance.true_rand_int(100, 1)
	>>> next(true_rand_int)
