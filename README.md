# heo_challenge_david_kim


# get_tle.py does one thing only: 
make an API call to space-tract and retrieve the TLE raw data. It gets cleaned up in plot_mean_alt.py.

# plot_mean_alt.py does three things: 
1. Read and clean the raw TLE data from get_tle.py, 
2. Perform math on the data cleaned from step 1 to get average altitude, 
3. collect information to plot and visualise it using matplotlib

I justified using Anthropic's Claude because it writes clean code, gives me someone to rubber duck my thoughts with, saves time, and is capable of checking and improving the code that I've written while explaining it