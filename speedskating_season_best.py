# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 08:50:56 2024

@author: Daan Wielens
"""
import urllib
import numpy as np
from matplotlib import pyplot as plt

'''
Test IDs:
- Myrthe Grobbink     92768
- Marit Grobbink      83441
'''
#%% Retrieve and parse data
list_distances = [100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000] # List of distances that should be checked
start_year = 2008 # Start with season 2018-2019
end_year = 2023 # End with season 2023-2024
IDs = [831] # IDs of all skaters that are analysed
names = ['Sven Kramer']  # Names corresponding to IDs
results = [] # Object to hold data

for user in zip(IDs, names):
    # Add user to results list
    user_values = [user[0], user[1]]
    results.append(user_values)

    # Retrieve data
    data = str(urllib.request.urlopen((r'https://speedskatingresults.com/api/xml/season_bests?skater=' + str(user[0]) + '&start=' + str(start_year) + '&end=' + str(end_year))).read())
    
    # Parse data - create own parser
    pr_matrix = np.array([0, 100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000], dtype='float')
    data = data.split('<')
    dist = 0
    for line in data:
        # Create new line to hold data for one season
        if 'season start' in line:
            pr_year = np.array([float(line.split('"')[1]), 0, 0, 0, 0, 0, 0, 0, 0, 0])
        # Determine what distance will be reported next
        if line == 'distance>100':
            dist = 100
        elif line == 'distance>300':
            dist = 300
        elif line == 'distance>500':
            dist = 500
        elif line == 'distance>700':
            dist = 700
        elif line == 'distance>1000':
            dist = 1000
        elif line == 'distance>1500':
            dist = 1500
        elif line == 'distance>3000':
            dist = 3000
        elif line == 'distance>5000':
            dist = 5000
        elif line == 'distance>10000':
            dist = 10000
        # Retrieve result for given distance
        if 'time>' in line and not '/' in line:
            time = line.split('>')[1]
            # Convert result into seconds
            time_split = time.split('.')
            if len(time_split) > 1:
                time_mins = float(time.split('.')[0])
                time_secs = float(time.split('.')[1].replace(',','.'))
                time = time_mins * 60 + time_secs
            else:
                time = float(time.replace(',','.'))
            
            # Store result in data line
            if dist == 100:
                pr_year[1] = time
            elif dist == 300:
                pr_year[2] = time
            elif dist == 500:
                pr_year[3] = time
            elif dist == 700:
                pr_year[4] = time
            elif dist == 1000:
                pr_year[5] = time
            elif dist == 1500:
                pr_year[6] = time 
            elif dist == 3000:
                pr_year[7] = time 
            elif dist == 5000:
                pr_year[8] = time 
            elif dist == 10000:
                pr_year[9] = time                 
        # At end of season, merge data line to pr matrix
        if '/season' in line:
            pr_matrix = np.vstack((pr_matrix, pr_year))
    
    # Finally, add matrix to user
    results[-1].append(pr_matrix)
    
#%% Store data to text file
with open('IJSCH_results.csv', 'w') as file:
    for i in range(len(results)):
        file.write(str(results[i][0]) + ' - ' + results[i][1] + '\n')
        n_years = np.size(results[i][2], 0)
        for j in range(n_years):
            datastr = np.array2string(results[i][2][j,:], separator=', ')[1:-1].replace('\n','').replace("'", '')
            file.write(datastr + '\n')
            
#%% Create line plots and table plots
'''
For every user, plot every distance. Set x-axis to start_year --> end_year
Only create a figure if a distance contains at least 2 points
Replace 0 values by NaN to avoid plotting
Convert y-axis back to min.sec,subsec?
'''

# Loop over user, then over distance
for i in range(len(results)):
    for j in range(len(list_distances)):
        username = results[i][1]
        distance = list_distances[j]
        year_vals = results[i][2][1:,0]
        time_vals = results[i][2][1:,j+1]
        for k in range(len(time_vals)):
            if time_vals[k] == 0:
                time_vals[k] = np.nan
        # Only plot if more than two time values are available
        if np.count_nonzero(~np.isnan(time_vals)) > 1:
            # Remove all nan-points from both lists
            year_vals = year_vals[~np.isnan(time_vals)]
            time_vals = time_vals[~np.isnan(time_vals)]
            
            plt.figure()
            plt.plot(year_vals, time_vals, '.--')
            plt.xlim([start_year-1, end_year+1])
            # Generate xticks
            year_list = np.arange(start_year, end_year+1)
            tick_str = []
            for n in range(len(year_list)):
                tick_str.append("'" + str(int(year_list[n] - 2000)) + "/'" + str(int(year_list[n] - 1999)))
            plt.xticks(year_list, tick_str, rotation=45)
     
            plt.ylim([0.95*np.nanmin(time_vals), 1.1*np.nanmax(time_vals)])
            plt.xlabel('Seizoen')
            plt.ylabel('Tijd (s)')
            # Add plot labels, formatted
            for m, txt in enumerate(time_vals):
                if not np.isnan(txt):
                    txt_min = int(np.floor(txt / 60))
                    if txt_min > 0:
                        txt_sec = str(np.round(txt % 60, 2))
                        txt_sec_int = int(txt_sec.split('.')[0])
                        txt_sec_subsec = txt_sec.split('.')[1]
                        txt = str(txt_min) + ':' + f'{txt_sec_int:02d}' + '.' + txt_sec_subsec # String-format txt_sec to get leading zero
                    plt.annotate(txt, (year_vals[m], time_vals[m]))

            plt.title(username + ' - ' + str(distance) + ' m')
            plt.tight_layout()
            plt.savefig(username.replace(' ','_') + '_' + str(distance) + '.png')
            plt.close()

#%% Create table plots
for i in range(len(results)):
    username = results[i][1]
    fig, ax = plt.subplots(figsize=(10,3))
    ax.xaxis.set_visible(False) 
    ax.yaxis.set_visible(False)
    ax.axis("off")
    
    # Format table
    pr_table_float = np.round(results[i][2][1:,1:], 2)
    pr_table = pr_table_float.astype(str)
    for p in range(np.size(pr_table, 0)):
        for q in range(np.size(pr_table, 1)):
            if pr_table_float[p,q] > 60:
                txt_min = int(np.floor(pr_table_float[p,q] / 60))
                txt_sec = str(np.round(pr_table_float[p,q] % 60, 2))
                txt_sec_int = int(txt_sec.split('.')[0])
                txt_sec_subsec = txt_sec.split('.')[1]
                txt = str(txt_min) + ':' + f'{txt_sec_int:02d}' + '.' + txt_sec_subsec 
                pr_table[p,q] = txt
            elif pr_table[p,q] == 'nan':
                pr_table[p,q] = ''
            else:
                pr_table[p,q] = str(pr_table_float[p,q])
                
    # Generate xticks
    year_list = results[i][2][1:,0]
    tick_str = []
    for n in range(len(year_list)):
        tick_str.append("'" + str(int(year_list[n] - 2000)) + "/'" + str(int(year_list[n] - 1999)))
    
    ax.table(pr_table, rowLabels=tick_str, colLabels=['100 m', '300 m', '500 m', '700 m', '1000 m', '1500 m', '3 km', '5 km', '10 km'], loc='center')
    ax.set_title(username)
    fig.tight_layout()
    fig.savefig(username.replace(' ','_') + '_table.png')
    
plt.close('all')
    
        


