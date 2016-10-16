# ghettotcx

GhettoTCX will parse a TCX file from Garmin, MapMyRide, etc.
and generate some basic plots.

The most interesting plot type is the heart rate zone chart.

It can create a panel of plots, by parsing all the files in a
given directory.


It's called GhettoTCX because it's no-frills, nothing fancy, not even a true
TCX file parser. It simply searches for some keywords and pulls out heartbeat
info and lat/long data. And not even at the same time, you need to the read
the file twice if you want to plot both.

There are "better" TCX/XML file parsers out there.  This one was meant to do
one thing (actually two things), quickly and easily:  plot heart rate (and
heart rate zones).  It can also plot lat/long data points onto a scatterplot,
but seriously no-frills when you can get nice google maps charts on MapMyRide
and practically any other fitness app out there.

It started out (and ended) as a fun weekend programming project... if you are
curious about your heart rate zone, and are too cheap (I mean cost-conscious)
to pay the monthly subscription fee to MapMyRide for the heart rate zone
chart, you can use this free tool instead.  Enjoy!



## Quick Start


#### Installation
Git clone the repo and then run this command: (use of a virtualenv is highly encouraged).

```
pip install .
```

#### Get your TCX Files

Go to MapMyRide, garmin, etc. and download the TCX files you want to analyse.
Save them all in a directory on your harddrive.  GhettoTCX can open all the
TCX files in a given directory for you.

#### Checkout the example ipython notebook

Look at ``tcx-example.ipynb`` for how to use the tool.


