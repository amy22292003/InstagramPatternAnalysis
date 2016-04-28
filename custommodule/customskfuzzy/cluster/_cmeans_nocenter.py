"""
cmeans.py : Fuzzy C-means clustering algorithm.
"""
import numpy as np
import sys
from scipy.spatial.distance import cdist

# data1:coordinate; similarity2:tag intersect similarity
def _cmeans0_ori(distance, u2, c, m, *para):
	# the kth for each cluster
	k = para[0]

	# Normalizing, then eliminating any potential zero values.
	u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	u_old = np.fmax(u_old, np.finfo(np.float64).eps)

	um = u_old ** m

	# remain the belonging rate >= the k-th max location of each cluster in um_c
	filter_k = lambda row:row < sorted(row, reverse=True)[k-1]
	fail_indices = np.apply_along_axis(filter_k, axis=1, arr=u)
	print("fail_indices:", fail_indices.shape, fail_indices[0:2, 0:4])

	# Calculate the average distance from entity to cluster 
	d = fail_indices.dot(distance) / np.ones((distance.shape[1],1)).dot(np.atleast_2d(fail_indices.sum(axis=1))).T
	print("d:", d.shape, d[0:3, 0:3])

	d = np.fmax(d, np.finfo(np.float64).eps)
	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return u, jm, d

def _distance(data, centers):
	return cdist(data, centers).T


def _fp_coeff(u):
	n = u.shape[1]

	return np.trace(u.dot(u.T)) / float(n)

def cmeans(distance, c, m, error, maxiter, algorithm, *para):
	init = None
	seed = None
	# Setup u0
	if init is None:
		if seed is not None:
			np.random.seed(seed=seed)
		n = distance.shape[0]
		u0 = np.random.rand(c, n)
		u0 /= np.ones(
			(c, 1)).dot(np.atleast_2d(u0.sum(axis=0))).astype(np.float64)
		init = u0.copy()
	u0 = init
	u = np.fmax(u0, np.finfo(np.float64).eps)

	# Initialize loop parameters
	jm = np.empty(0)
	p = 0

	#select cmeans function
	if algorithm is "Original":
		_cmeans0 = _cmeans0_ori
	else:
		print("Error, nonexistent fuzzy c means algorithm:", algorithm)
		sys.exit()

	# Main cmeans loop
	while p < maxiter - 1:
		print(p, "---------------------------->")
		u2 = u.copy()
		[u, Jjm, d] = _cmeans0(distance, u2, c, m, *para)
		jm = np.hstack((jm, Jjm))
		p += 1

		# Stopping rule
		if np.linalg.norm(u - u2) < error:
			break

	print("end u.sum:", u.sum(axis=0), u.sum(axis=1))
	print("Fin u>>\n", u[:,0],u[:,1], u[:,2], "\nu std:", np.std(u))
	# Final calculations
	error = np.linalg.norm(u - u2)
	fpc = _fp_coeff(u)

	return u, u0, d, jm, p, fpc
