[![Build Status](https://travis-ci.org/simongarisch/safeqthreads.svg?branch=master)](https://travis-ci.org/simongarisch/safeqthreads)
[![Coverage Status](https://coveralls.io/repos/github/simongarisch/safeqthreads/badge.svg?branch=master)](https://coveralls.io/github/simongarisch/safeqthreads?branch=master)

# safeqthreads

The motivation behind safeqthreads is to allow Qthreads to finish before the application exits. If the application exits before a QThread is finished the Python garbage collector will release the QThread and potentially cause Python to crash.

## Installation
safeqthreads is both python 2 and 3 compatible
```bash
pip install safeqthreads
```

## Motivation
...

## Examples
...
