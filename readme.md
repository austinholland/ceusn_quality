# CEUSN Quality Assessment

The routines here take advantage of IRIS Mustang metrics and evaluate the performance
and resolution for networks in the CEUSN.  This is just a quick tool that will be updated
in the future to be more interactive.

## Configuration

The behavior of the scripts are controlled by a config file in json format.  This may be 
added effort, but it will make things easier down the road (hopefully).
For this example "ceusn_config.json"

## Data

For all metrics we are looking at the 2016 calendar year so 2016-0101 through 2016-12-31. 
We use the PDF noise downloaded from IRIS to generate some DQA style metrics as well as
examine possible magnitude of completeness/detection thresholds in the region covered by 
the N4 network.  We also use mustang metrics to provide data availability and gaps per day.

We use DQA metrics for the aggregate score from Ringler et al. (2015) for those metrics 
included in that paper.  For those metrics that are not included in the paper, I followed
the method described in Appendix A of the paper to create a grading scale.  This allows 
for the greatest comparison.  The method for calculating the grading can be seen in score.py 
which had some modifications due to bad values and more data.

* Number of Channels: 2748
* From 1.000000 percentile to 61.000000 percentile
* NLNM 0.5 - 1 s Period Deviation p2: 16.073476, m: 10.538043
* NLNM 0.125 - .25 s Period Deviation p2: 16.355719, m: 17.022342

The raw data downloaded from IRIS is stored in the data directory.
* data/NN/ - stored as raw downloaded text by NSLC-pdf.txt


## TODO

1. Examine accelerometer distributions surrounding potential source zones identified by the 
NSHM.

## Python Files

*  pull_noisepdf.py - pulls PDF noise as text files from IRISWS
*  utils.py - routines common among the different processing routines
*  noise.py - library to calculate NLNM at different periods
*  statcalc.py - Define the SQLAlchemy tables for saving data and calculate channel metrics
*  score.py - Calculate scoring parameters for high frequency nlnm metrics