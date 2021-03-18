#!/usr/bin/env python

'''
Adapted from geopriv4j (Java) packaged: https://dl.acm.org/doi/pdf/10.1145/3403896.3403968 (Fan and Gunja, 2020);
/*
 * In this method we will be generating a new location (z) with a probability (p) that 
 * reduces as the distance increase within a certain radius (r).
 * 
 * As in Geopriv4j, this algorithm is based on the paper by Andrés, Miguel E., et al. 
 * "Geo-indistinguishability: Differential privacy for location-based systems." 
 * Proceedings of the 2013 ACM SIGSAC conference on Computer & communications 
 * security. 2013. https://doi.org/10.1145/2508859.2516735
'''

import numpy as np
#Define constant earth radius
earth_radius = 6.3781e6

#Convert degrees to radians
def rad_of_deg(ang):
	return np.radians(ang)

#Convert radians to degrees
def deg_of_rad(ang):
	return np.degrees(ang)
	
#Define Lambda distribution
def LambertW(x):
	#Min diff decides when the while loop ends
	min_diff = 1e-10
	if (x == -1 / np.e):
		return -1
	elif ((x < 0) and (x > -1/np.e)):
		q = np.log(-x)
		p = 1
		while (abs(p-q) > min_diff):
			p = (q * q + x / np.exp(q)) / (q + 1)
			q = (p * p + x / np.exp(p)) / (p + 1)
		#determine the precision of the float number to be returned
		return (np.round(1000000 * q) / 1000000)
	elif (x == 0):
		return 0
	else:
		return 0

def inverseCumulativeGamma(epsilon,z):
	x = (z - 1) / np.e
	return -(LambertW(x) + 1)/epsilon

def alphaDeltaAccuracy(epsilon,delta):
	return inverseCumulativeGamma(epsilon,delta)
	
def expectedError(epsilon):
	return 2/epsilon

def addPolarNoise(epsilon,lng,lat):
	#Random number in [0, 2*pi)
	theta = np.random.rand()*np.pi*2	
	#Random number in [0,1)
	z = np.random.rand()
	r = inverseCumulativeGamma(epsilon,z)
	return addVectorToPos(lng,lat,r,theta)

def addVectorToPos(lng,lat,distance,angle):
	ang_distance = distance / earth_radius
	lat1 = rad_of_deg(lat)
	lon1 = rad_of_deg(lng)
	lat2 = np.arcsin(np.sin(lat1)*np.cos(ang_distance) + np.cos(lat1)*np.sin(ang_distance)*np.cos(angle))
	lon2 = lon1 + np.arctan2(np.sin(angle)*np.sin(ang_distance)*np.cos(lat1),np.cos(ang_distance)-np.sin(lat1)*np.sin(lat2))
	lon2 = (lon2 + 3*np.pi) % (2*np.pi) - np.pi #Normalize to -180 to +180
	latnew = deg_of_rad(lat2)
	lngnew = deg_of_rad(lon2)
	return lngnew,latnew

#Geoindistinguishability algorithm
class LaplaceAlgorithm:
	#Init
	def __init__(self,epsilon=0.1):
		self.epsilon = epsilon

	def generate(self,lng,lat):
		#print(str(lng)+','+str(lat)+','+str(self.epsilon))
		return addPolarNoise(self.epsilon, lng, lat)
