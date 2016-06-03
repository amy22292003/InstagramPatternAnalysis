"""
cmeans.py : Fuzzy C-means clustering algorithm.
"""
import datetime
import numpy as np
import random
import sys
from scipy.spatial.distance import cdist
from . import distance as cdistance

def _cmeans0_2distw(data1, u_old, c, m, level, *para):
	# the kth for each cluster
	k = para[0]
	data2 = para[1]
	w = para[2]
	#print("--u.sum:", u_old.sum(axis=1))

	# Normalizing, then eliminating any potential zero values.
	um = u_old / np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	um = np.fmax(um, np.finfo(np.float64).eps)
	um = um ** m

	# get distance to each cluster center sequences
	d1 = []
	d2 = []

	for c_i in range(c):
		large_k = [i for i, x in enumerate(u_old[c_i,:]) if x >= sorted(u_old[c_i,:], reverse=True)[k - 1]]
		print("   ", c_i, "- origin large k:",  len(large_k))
		if len(large_k) > k:
			large_k = random.sample(large_k, k)

		target1 = np.array(data1)[large_k]
		distance1 = cdistance.get_distance(level, data1, target1)
		d1.append(np.sum(distance1, axis=0) / distance1.shape[0])

		target2 = np.array(data2)[large_k]
		distance2 = cdistance.get_distance(level, data2, target2)
		d2.append(np.sum(distance2, axis=0) / distance2.shape[0])

	d1 = np.array(d1) / np.std(d1)
	d2 = np.array(d2) / np.std(d2)
	#print("d2:", d2[0:3, 0:5], " max:", np.amax(d2), " min:", np.amin(d2))

	d = w * d1 + (1 - w) * d2
	#print("d:", d[0:3, 0:5], " max:", np.amax(d), " min:", np.amin(d))

	d = np.fmax(d, np.finfo(np.float64).eps)
	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return u, jm, d

def _fp_coeff(u):
	n = u.shape[1]

	return np.trace(u.dot(u.T)) / float(n)

def cmeans(data, c, m, error, maxiter, algorithm, level, *para, init = None, seed = None):
	# Setup u0
	if init is None:
		if seed is not None:
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
	print("u.shape:", u.shape, u.shape[0] * u.shape[1])

	#select cmeans function
	if algorithm is "2WeightedDistance":
		_cmeans0 = _cmeans0_2distw
	else:
		print("Error, nonexistent fuzzy c means algorithm:", algorithm)
		sys.exit()

	error_list = []
	# Main cmeans loop
	while p < maxiter - 1:
		print("--", p, "----------------------------> ", datetime.datetime.now())
		u2 = u.copy()
		[u, Jjm, d] = _cmeans0(data, u2, c, m, level, *para)
		jm = np.hstack((jm, Jjm))
		p += 1
		error_list.append(np.linalg.norm(u - u2) / (u.shape[0] * u.shape[1]))

		# Stopping rule
		if np.linalg.norm(u - u2) / (u.shape[0] * u.shape[1]) < error:
			break
	print("  error:", error_list)
	print("  error avg:", sum(error_list) / len(error_list))

	print("--End> u.sum:", u.sum(axis=0)[0:6], u.sum(axis=1))
	print("  Fin u>>\n", u[:,0],u[:,1], u[:,2], "\n  u avg:", np.sum(u) / (u.shape[0] * u.shape[1]), "\nu std:", np.std(u))
	# Final calculations
	error = np.linalg.norm(u - u2)
	fpc = _fp_coeff(u)

	return u, u0, d, jm, p, fpc
