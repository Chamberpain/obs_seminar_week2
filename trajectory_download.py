import os
import pandas as pd
from ftplib import FTP 
import oceans
import requests
import datetime
import sys, os
sys.path.append(os.path.abspath("../eulerian_plot/Basemap/"))
from eulerian_plot import *
import matplotlib.pyplot as plt

def download_meta_file_and_compile_df():
	filename = 'ar_index_global_prof.txt'
	try:
		df_ = pd.read_csv(filename,skiprows=8)
	except:
		link = 'usgodae.org'
		ftp = FTP(link) 
		ftp.login()
		ftp.cwd('pub/outgoing/argo')
		
		file = open(filename, 'wb')
		ftp.retrbinary('RETR %s' % filename,file.write,8*1024)
		file.close()
		ftp.close()
		df_ = pd.read_csv(filename,skiprows=8)
	df_['Cruise'] = [dummy.split('/')[1] for dummy in df_['file'].values]
	# df_ = df_[df_.date!='I'] # munging the dataset
	#but this was not necessary
	df_ = df_.dropna(subset=['date'])
	df_['date'] = pd.to_datetime(df_['date'].astype(int),format='%Y%m%d%H%M%S')
	# parse the data to our time and region of interest
	df_ = df_[df_.date<datetime.date(2009,1,1)] # this is the date the paper was submitted
	df_ = df_[df_.date>=datetime.date(2002,1,1)] # this is the date the paper was submitted
	df_ = df_[df_.longitude!=99999]
	df_ = df_[df_.longitude!=-999]
	df_ = df_[df_.longitude<=180]
	df_ = df_[df_.latitude<=-35]
	df_ = df_[df_.latitude>=-65]

	# include some checks on the data
	assert (df_.date>datetime.date(1997,1,1)).all()
	assert df_.longitude.min()>-180
	assert df_.longitude.max()<=180
	assert df_.latitude.min()>-90
	assert df_.latitude.max()<90
	df_['Lon'] = df_.longitude
	df_['Lat'] = df_.latitude
	df_['Date'] = df_.date
	df_ = df_[['Lat','Lon','Cruise','Date']]
	df_.to_pickle('traj_df.pickle')
	print('trajectory data has been downloaded and recompiled')
	return df_


try:
	df = pd.read_pickle('traj_df.pickle')
except IOError:
	print('No trajectory dataframe found, redownloading and recompiling trajectory dataframe')
	df = download_meta_file_and_compile_df()

plt.figure(figsize=(10,10))
m = SBasemap(resolution='h',region='polar',dataframe=df)
m.scatter(df.Lon.values,df.Lat.values,latlon=True,s=0.1)
m.orsi_fronts()
m.linespace()
plt.title('All argo profiles in southern ocean')
plt.savefig('all_argo.png')
plt.close()
number_of_profiles = []
for month_num in [dummy + 1 for dummy in range(12)]:
	df_token = df[df.Date.dt.month==month_num]
	number_of_profiles.append(len(df_token))
	plt.figure(figsize=(10,10))
	m = SBasemap(resolution='h',region='polar',dataframe=df_token)
	m.scatter(df_token.Lon.values,df_token.Lat.values,latlon=True,s=0.1)
	m.orsi_fronts()
	m.linespace()
	plt.title('Argo profiles in southern ocean for month '+str(month_num))
	plt.savefig('argo_month_'+str(month_num)+'.png')
	plt.close()
plt.plot([dummy + 1 for dummy in range(12)],number_of_profiles/((np.cos(np.deg2rad(25))-np.cos(np.deg2rad(55)))*2*np.pi*6371**2)*1879) #1879 is their grid size in km^2
plt.ylabel('Number Profiles')
plt.xlabel('Month')
plt.title('Number of Profiles per grid box')
plt.savefig('number_of_profiles_by_month')
plt.close()
#downloaded from 'https://www.esrl.noaa.gov/psd/data/20thC_Rean/timeseries/monthly/SAM/sam.20crv2c.long.data'
#then converted to RTF format
file = 'sam.20crv2c.txt'
df_sam = pd.read_csv(file,skiprows=9,sep='\s+')   
df_sam = df_sam[['Year','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].dropna()
df_sam['Dec'] = [dummy[:-1] for dummy in df_sam['Dec'].values.tolist()]
df_sam['Year'] = df_sam['Year'].astype(int)
df_sam = df_sam.set_index('Year')
df_sam = df_sam[(df_sam.index>=2002)&(df_sam.index<=2009)]	
df_sam[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']] = df_sam[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].astype(float)
sam_std = df_sam[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].values.std()/2
df_sam.mean().plot(use_index='True')
plt.title('SAM mean index by month')
plt.ylabel('Sam Index')
plt.xlabel('Month')
ind = [1+dummy for dummy in range(12)]
name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
ax.set_xticks(ind)
ax.set_xticklabels(ind)
plt.savefig('mean_sam_index_month.png')


month_lib = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
for year in df.Date.dt.year.unique():
	for month in df.Date.dt.month.unique():
		mask = (df.Date.dt.month==month)&(df.Date.dt.year==year)
		df.loc[mask,'SAM'] = df_sam[df_sam.index==year][month_lib[month]].values[0]

number_of_profiles = []
for df_token,title in [(df[df['SAM']>sam_std/2],'Positive'),(df[df['SAM']<-sam_std/2],'Negative')]:
	number_of_profiles.append(len(df_token))
	plt.figure(figsize=(10,10))
	m = SBasemap(resolution='h',region='polar',dataframe=df_token)
	m.scatter(df_token.Lon.values,df_token.Lat.values,latlon=True,s=0.1)
	m.orsi_fronts()
	m.linespace()
	plt.title('Argo profiles for '+str(title)+' SAM')
	plt.savefig('argo_profiles_sam_'+str(title)+'.png')
	plt.close()
fig, ax = plt.subplots()
ind = (1,2)
ax.bar(ind,number_of_profiles/((np.cos(np.deg2rad(25))-np.cos(np.deg2rad(55)))*2*np.pi*6371**2)*1879)
plt.ylabel('Number Profiles')
ax.set_xticks(ind)
ax.set_xticklabels(('Positive SAM', 'Negative SAM'))
plt.title('Number of Profiles per grid box')
plt.savefig('number_of_profiles_by_SAM')
plt.close()