
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[25]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[26]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[27]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3
    A recession is defined as starting with two consecutive quarters of GDP decline, 
    and ending with two consecutive quarters of GDP growth.'''
    gdp = pd.read_excel('gdplev.xls', skiprows = 7, usecols= {'Unnamed: 4', 'Unnamed: 6'})
    gdp = gdp.loc[212:]
    gdp = gdp.rename(columns = {'Unnamed: 4': 'Quarter', 'Unnamed: 6': 'GDP'})
    gdp['GDP'] = pd.to_numeric(gdp['GDP'])
    global gdp
    quarters = []
    for i in range(len(gdp) - 2):
        if (gdp.iloc[i][1] > gdp.iloc[i+1][1]) & (gdp.iloc[i+1][1] > gdp.iloc[i+2][1]):
            quarters.append(gdp.iloc[i+1][0])
    return quarters[0]

get_recession_start()


# In[28]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    #figured out that gdp[gdp['Quarter'] == '2008q2'].index.tolist() was [245]
    gdp2 = gdp.loc[245:]
    recession_end = []
    for i in range(len(gdp2)- 2):
        if (gdp2.iloc[i+2][1] > gdp2.iloc[i+1][1])  & (gdp2.iloc[i+1][1] > gdp2.iloc[i][1]):
            recession_end.append(gdp2.iloc[i+2][0])
    return recession_end[0]

get_recession_end()


# In[29]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    recession_period = gdp.loc[245:]
    recession_min = recession_period[recession_period['GDP'] == recession_period['GDP'].min()]
    return recession_min.values[0][0]

get_recession_bottom()


# In[30]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )'''
    with open('university_towns.txt') as file:
        data = []
        for line in file:
            data.append(line[:-1])
    state_town = []
    for line in data:
        if line[-6:] == '[edit]':
            state = line[:-6]
        elif '(' in line:
            town = line[:line.index('(')-1]
            state_town.append([state,town])
        else:
            town = line
            state_town.append([state,town])
    state_college_df = pd.DataFrame(state_town,columns = ['State','RegionName'])
    return state_college_df

get_list_of_university_towns()


# In[31]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    housingdata_df = pd.read_csv('City_Zhvi_AllHomes.csv')
    #convert two-letter-state to full name of state
    housingdata_df['State'] = housingdata_df['State'].map(states)
    #set index to state, regionname
    housingdata_df.set_index(["State","RegionName"], inplace=True)
    #filter columns by year, only want 2000 to 2016
    housingdata_df = housingdata_df.filter(regex='^20', axis=1)
    #group select columns by quarter, calculates average per quarter
    housingdata_df = housingdata_df.groupby(pd.PeriodIndex(housingdata_df.columns, freq='Q'), axis=1).mean()
    global housingdata_df
    return housingdata_df

convert_housing_data_to_quarters()


# In[32]:

#grabbed results from earlier funcs
recession_start = get_recession_start()
recession_bottom = get_recession_bottom()
university_towns = get_list_of_university_towns()

housingdata_df = convert_housing_data_to_quarters().dropna()
hdf = housingdata_df.copy()

#create ratio of housing prices from recession start to recession bottom
ratio = pd.DataFrame({'ratio': hdf[recession_start].div(hdf[recession_bottom])})

#ratio will not append since not recognized as PeriodIndex
#change dataframe to str, then concatenated ratio to hdf
hdf.columns = hdf.columns.to_series().astype(str)
hdf = pd.concat([hdf, ratio], axis=1)

#converted it back to hdf
hdf = pd.DataFrame(hdf)
hdf.reset_index(['State','RegionName'], inplace = True)

#spliced dataframe to unitown and non-unitown, calculated ratios for each, dropped NaN values
unitown_priceratio = hdf.loc[list(university_towns.index)]['ratio'].dropna()
nonunitown_priceratio_index = set(hdf.index) - set(unitown_priceratio)
nonunitown_priceratio = hdf.loc[list(nonunitown_priceratio_index),:]['ratio'].dropna()

def run_ttest(a, b):
    '''First create new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then run a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivalent to a
    reduced market loss).'''
    
    #run t-test comparing university town values to non-university town values
    tstat, p = tuple(ttest_ind(a, b))
    
    #return tuple where different = True or False, return p-value, and whether university-town is better or not
    different = p < 0.05
    result = tstat < 0
    better = ["university town", "non-university town"]
    
    return (different, p, better[result])
    
run_ttest(unitown_priceratio, nonunitown_priceratio)
