"""
cmeans.py : Fuzzy C-means clustering algorithm.
"""
from collections import deque
import datetime
import numpy as np
import random
import sys
from scipy.spatial.distance import cdist
from . import distance as cdistance

"""parameters"""
RAND_SEED_INIT = 0
RAND_SEED_K = 0

def _cmeans0_2distw(data1, u_old, c, m, level, *para):
	# the kth for each cluster
	k = para[0]
	data2 = para[1]
	w = para[2]

	# Normalizing, then eliminating any potential zero values.
	um = u_old / np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	um = np.fmax(um, np.finfo(np.float64).eps)
	um = um ** m

	# get large k indices for each cluster
	filter_k = lambda row:row >= sorted(row, reverse=True)[k - 1] # get the indices which fit the condition
	large_k = np.apply_along_axis(filter_k, axis=1, arr=u_old)

	large_k_indices = deque()
	random.seed(RAND_SEED_K)
	for i in range(c):
		indices = list(np.nonzero(large_k[i, :])[0])
		if len(indices) > k:
			rand_k = random.sample(indices, k)
			large_k_indices.extend(rand_k)
		else:
			large_k_indices.extend(indices)
	print("  unique center #:", len(set(large_k_indices)))
	print("  center:", large_k_indices)

	# get distances between targets(c# * k) & data
	distance1 = _distance(level, data1, large_k_indices)
	distance2 = _distance(level, data2, large_k_indices)

	# calculate data to each cluster's average distance
	each_cluster = np.zeros((c, c))
	np.fill_diagonal(each_cluster, 1)
	each_cluster = np.repeat(each_cluster, k, axis = 1)
	d1 = each_cluster.dot(distance1) / k
	d2 = each_cluster.dot(distance2) / k

	d = w * d1 + (1 - w) * d2
	#print("  d:", d.shape, d[0:3, 0:5], " max:", np.amax(d), " min:", np.amin(d))

	d = np.fmax(d, np.finfo(np.float64).eps)
	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return u, jm, d, large_k_indices

def _distance(level, data, target_indices):
	targets = np.array(data)[target_indices]
	distance = cdistance.get_distance(level, data, targets)
	#distance = distance / np.amax(distance)
	return distance

def _fp_coeff(u):
	n = u.shape[1]

	return np.trace(u.dot(u.T)) / float(n)

def cmeans(data, c, m, error, maxiter, algorithm, level, *para, init = None, seed = RAND_SEED_INIT):
	# Setup u0
	if init is None:
		np.random.seed(seed=seed)
		n = len(data)
		u0 = np.random.rand(c, n)
		u0 /= np.ones(
			(c, 1)).dot(np.atleast_2d(u0.sum(axis=0))).astype(np.float64)
		init = u0.copy()
	u0 = init
	u = np.fmax(u0, np.finfo(np.float64).eps)

	# Initialize loop parameters
	jm = np.empty(0)
	p = 0
	print("--u.shape:", u.shape, ", elements:", u.shape[0] * u.shape[1])

	#select cmeans function
	if algorithm is "2WeightedDistance":
		_cmeans0 = _cmeans0_2distw
	else:
		print("Error, nonexistent fuzzy c means algorithm:", algorithm)
		sys.exit()

	error_list = []
	# Main cmeans loop
	while p < maxiter - 1:
		print("--", p, "-----------------------------------------> ", datetime.datetime.now())
		u2 = u.copy()
		[u, Jjm, d, center] = _cmeans0(data, u2, c, m, level, *para)
		jm = np.hstack((jm, Jjm))
		p += 1
		error_list.append(np.linalg.norm(u - u2) / (u.shape[0] * u.shape[1]))

		# Stopping rule
		if np.linalg.norm(u - u2) / (u.shape[0] * u.shape[1]) < error:
			break
	print("-------------------------------")
	print("  error:", error_list)
	print("  >>> p=", p)
	print("  error avg:", sum(error_list) / len(error_list), ", max/min:", max(error_list), min(error_list))
	print("  Fin u>>\n", u[:,0:2], "\n  u avg:", np.sum(u) / (u.shape[0] * u.shape[1]), "\n  u std:", np.std(u))
	# Final calculations
	error = np.linalg.norm(u - u2)
	fpc = _fp_coeff(u)

	return u, u0, d, jm, p, fpc, center
