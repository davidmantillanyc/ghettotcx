
# ghettotcx.py
#
# MIT License
# 
# Copyright (c) 2016 David Mantilla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE


"""
tcx.py

Ghetto TCX will parse a TCX file from Garmin, MapMyRide, etc.
and generate some basic plots.

The most interesting plot type is the heart rate zone chart.

It can create a panel of plots, by parsing all the files in a
given directory.

"""

import os
from xml.etree.ElementTree import iterparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# For debugging/testing purposes:
FILEDIRECTORY='./example_data'
FILENAME='example.tcx'
FILEPATH=os.path.join(FILEDIRECTORY, FILENAME)


class TCX(object):
    """interface for objects that parse TCX files"""
    _df = None

    def __init__(self, filepath=FILEPATH):
        """ load a TCX from a filepath """
        print "Loading", filepath, "..."
        self._df = self._get_dataframe(os.path.join(filepath))

    @classmethod
    def load_directory(cls, directorypath=FILEDIRECTORY, class_factory=lambda x: None):
        """ load a all TCX files from a directory path using a factory pattern."""
        return [class_factory(os.path.join(directorypath, f)) for f in os.listdir(directorypath) if f.endswith(".tcx")]

    def _get_dataframe(self, filepath):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError


class HeartRate(TCX):

    def _heartrate_parser(self, filename):
        "return a list of values with timestamp, heart rate given a xml file"
        relevant_tags = ['{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value'
        ]
        group_name = ''
        counter = 0
        items = iterparse(filename, events=['start'])
        timevalue = ""
        heartrate = ""
        values = []
        for (event, node) in items:
            counter += 1
            if node.tag not in relevant_tags:
                # Ignore anything not part of the outline
                continue
            # Output a heartrate entry
            if node.tag:
                if node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time':
                    timevalue = node.text.strip() if node.text else np.nan
                elif node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm':
                    # grab next value
                    (event, node) = items.next()
                    if node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value':
                        heartrate = node.text.strip() if node.text else np.nan
                    val = (timevalue, heartrate)
                    values.append(val)
                else:
                    pass
        return values

    def _get_dataframe(self, filepath):
        "get dataframe of heart rate values given a TCX/XML file"
        values = self._heartrate_parser(filepath)
        df = pd.DataFrame(values)
        df.columns = ['timevalue', 'heartrate']
        df.timevalue = pd.to_datetime(df.timevalue)
        df.heartrate = pd.to_numeric(df.heartrate)
        df['zone'] = df.apply(self.zoneify, axis=1)
        self._df = df.dropna()
        return self._df

    def zoneify(self, x):
        if x['heartrate'] < 110:   return 1
        elif x['heartrate'] < 130: return 2
        elif x['heartrate'] < 145: return 3
        elif x['heartrate'] < 165: return 4
        elif x['heartrate'] > 165: return 5
        else:  return 0

    # TODO: Move to test file; this was old code
    def test_zoneify(self):
        """some unit tests because TDD is important ;) """
        tests = [({'heartrate': 0}, 1),
                 ({'heartrate': 111}, 2),
                 ({'heartrate': 135}, 3),
                 ({'heartrate': 150}, 4),
                 ({'heartrate': 200}, 5)]
        for test_input, expected in tests:
            assert(expected == zoneify(test_input))

    def plot(self, draw_plot=True, plt_=plt, fig_size=(5,5)):
        old_fig_size = plt.rcParams["figure.figsize"]
        plt.rcParams["figure.figsize"] = fig_size
        self.plot_heartrate(draw_plot=draw_plot, plt_=plt_)
        plt.rcParams["figure.figsize"] = old_fig_size


    def plot_heartrate(self, draw_plot = True, plt_=plt):
        plt_.plot(self._df['heartrate'])
        if draw_plot: plt_.show()

    def plot_heartrate_histogram(self, draw_plot=True):
        plotdata = plt.hist(self._df['heartrate'], bins=40)
        hist_x = plotdata[1][:-1] # one too many values in x values array, so trim it down
        hist_y = plotdata[0]
        if draw_plot: plt.show()
        return (hist_x, hist_y)

    def plot_heartratezone(self, draw_plot=True):
        dfg=self._df.groupby('zone').count()
        bars = plt.bar(dfg.index, dfg.heartrate)
        if draw_plot: plt.show()
        return bars

    @classmethod
    def create_heartrate_panel(cls, heartrate_list, fig_size=(12, 24), draw_plot=True):
        assert(isinstance(heartrate_list, list))
        old_fig_size = plt.rcParams["figure.figsize"]
        plt.rcParams["figure.figsize"] = fig_size


        num_rows = len(heartrate_list)
        _, pp = plt.subplots(num_rows, 2, sharex='col', sharey='col', squeeze=False)
        counter = 0
        for i, j in pp:
            # plot time series of heart rate
            heartrate_list[counter].plot_heartrate(draw_plot=False, plt_=i)
            # plot histogram
            x, y = heartrate_list[counter].plot_heartrate_histogram(draw_plot=False)
            j.bar(x, y)
            counter += 1

        plt.rcParams["figure.figsize"] = old_fig_size
        if draw_plot: plt.show()


class LatLong(TCX):
    """TCX file parser that plots Lat Long points on a scatterplot."""

    def _geoloc_parser(self, filename):
        """
        return a list of values with timestamp, heart rate given a xml file.
        file looks like:
                            <Trackpoint>
                            <Time>
                                2016-08-24T13:29:25.247000+00:00
                            </Time>
                            <Position>
                                <LatitudeDegrees>
                                    40.88494408
                                </LatitudeDegrees>
                                <LongitudeDegrees>
                                    -73.89171147
                                </LongitudeDegrees>
                            </Position>
                            <AltitudeMeters>
                                22.0
                            </AltitudeMeters>
                            <DistanceMeters>
                                0.0
                            </DistanceMeters>
                        </Trackpoint>
        """
        relevant_tags = ['{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LatitudeDegrees',
                        '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LongitudeDegrees',
        ]
        counter = 0
        items = iterparse(filename, events=['start'])
        values = []
        for (_, node) in items:
            counter += 1
            #if counter > 1000: break
            if node.tag not in relevant_tags:
                # Ignore anything not part of the outline
                continue
            # Output a heartrate entry
            if node.tag:
                if node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time':
                    timevalue = node.text.strip() if node.text else np.nan
                    (event, node) = items.next()
                    if node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position':
                        # grab next value
                        (event, node) = items.next()
                        if node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LatitudeDegrees':
                            latitude = node.text.strip() if node.text else np.nan
                        (event, node) = items.next()
                        if node.tag.strip() == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LongitudeDegrees':
                            longitude = node.text.strip() if node.text else np.nan
                        val = (timevalue, latitude, longitude)
                        values.append(val)
                else:
                    pass
        return values

    def _get_dataframe(self, filepath):
        "get dataframe of lat long values given a TCX/XML file"
        values = self._geoloc_parser(filepath)
        df = pd.DataFrame(values)
        df.columns = ['timevalue', 'latitude', 'longitude']
        df.timevalue = pd.to_datetime(df.timevalue)
        df.latitude = pd.to_numeric(df.latitude)
        df.longitude = pd.to_numeric(df.longitude)
        self._df = df.dropna()
        return self._df

    def plot(self, draw_plot=True, plt_=plt, fig_size=(5,5)):
        old_fig_size = plt.rcParams["figure.figsize"]
        plt.rcParams["figure.figsize"] = fig_size
        plt.scatter(self._df['longitude'], self._df['latitude'])
        if draw_plot: plt_.show()
        plt.rcParams["figure.figsize"] = old_fig_size


if __name__ == '__main__':

    # Load single file and create some plots
    h = HeartRate(FILEPATH)
    h.plot_heartrate()
    h.plot_heartrate_histogram()
    h.plot_heartratezone()

    # Plot all TCX files in a directory
    HeartRate.create_heartrate_panel(TCX.load_directory(class_factory=HeartRate))

    # Plot the long/lat points on a scatterplot
    l = LatLong(FILEPATH)
    l.plot()
