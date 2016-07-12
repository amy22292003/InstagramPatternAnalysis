"""
cmeans.py : Fuzzy C-means clustering algorithm.
"""
import numpy as np
import sys
from scipy.spatial.distance import cdist

"""parameters"""
RAND_SEED_INIT = 16

# data1:coordinate; similarity2:tag intersect similarity
def _cmeans0_ori(data, u_old, c, m, *para):
	"""
	Single step in generic fuzzy c-means clustering algorithm.
	data2 is for intersect counting
	"""
	# Normalizing, then eliminating any potential zero values.
	u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	u_old = np.fmax(u_old, np.finfo(np.float64).eps)

	um = u_old ** m

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	data = data.T
	cntr = um.dot(data) / (np.ones((data.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T)
	d = _distance(data, cntr) # euclidean distance

	d = np.fmax(d, np.finfo(np.float64).eps)
	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return cntr, u, jm, d

def _cmeans0_kth_lfreq(data, u_old, c, m, *para):
	"""
	Single step in generic fuzzy c-means clustering algorithm.
	data2 is for intersect counting
	"""
	# parameters
	k = para[0]
	location_frequency = para[1]

	# Normalizing, then eliminating any potential zero values.
	u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	u_old = np.fmax(u_old, np.finfo(np.float64).eps)

	um = u_old ** m

	# calculating u_c
	#u_c = u_old / u_old.sum(axis=1)[:,None]

	# remain the belonging rate >= the k-th max location of each cluster in um_c
	filter_k = lambda row:row < sorted(row, reverse=True)[k-1]
	fail_indices = np.apply_along_axis(filter_k, axis=1, arr=u_old)
	um[fail_indices] = 0

	# cluster freqeuncy
	true_indices = np.invert(fail_indices)
	cluster_frequency = true_indices.dot(np.atleast_2d(location_frequency).T)
	cluster_frequency = cluster_frequency / np.amax(cluster_frequency)

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	data = data.T
	cntr = um.dot(data) / (np.ones((data.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T)
	d = _distance(data, cntr) # euclidean distance

	"""
	data = data.T
	print("data.shape:", data.shape)
	dx = _distance(data, data) / np.ones((data.shape[0], 1)).dot(np.atleast_2d(location_frequency)).T
	print("um.shape:", um.shape, "dx.shape:", dx.shape, dx[0:5,0:2])
	print(" /.shape:", np.ones((data.shape[0],1)).dot(np.atleast_2d(um.sum(axis=1))).T.shape, np.ones((data.shape[0],1)).dot(np.atleast_2d(um.sum(axis=1))).T[0:5,0:3])
	d = um.dot(dx) / np.ones((data.shape[0],1)).dot(np.atleast_2d(um.sum(axis=1))).T
	print("d.shape:", d.shape, d[0:5,0:3])
	d = np.fmax(d, np.finfo(np.float64).eps)
	"""

	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1)) * cluster_frequency.dot(np.ones((1, d.shape[1])))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	#print("  - d:", d[0:5, 0:3], "\n  - u:", u[0:5, 0:3])
	return cntr, u, jm, d

def _distance(data, centers):
	return cdist(data, centers).T

def _fp_coeff(u):
	n = u.shape[1]

	return np.trace(u.dot(u.T)) / float(n)

def cmeans(data, c, m, error, maxiter, algorithm, *para, init = None, seed = RAND_SEED_INIT):
	"""
	data2 is for intersect counting
	"""
	# Setup u0
	if init is None:
		np.random.seed(seed=seed)
		n = data.shape[1]
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
	elif algorithm is "kthCluster_LocationFrequency":
		_cmeans0 = _cmeans0_kth_lfreq
	else:
		print("Error, nonexistent fuzzy c means algorithm:", algorithm)
		sys.exit()

	error_list = []
	# Main cmeans loop
	while p < maxiter - 1:
		if p % 100 == 0:
			print("-", p, "---------------------------->")
		u2 = u.copy()
		[cntr, u, Jjm, d] = _cmeans0(data, u2, c, m, *para)
		jm = np.hstack((jm, Jjm))
		p += 1
		error_list.append(np.linalg.norm(u - u2) / (u.shape[0] * u.shape[1]))

		# Stopping rule
		if np.linalg.norm(u - u2) / (u.shape[0] * u.shape[1]) < error:
			break
	print("  error:", error_list)
	print(">>> p=", p)
	#print("  Final u.sum:", u.sum(axis=0), "\n", u.sum(axis=1))
	#print("  Final u:>>\n", u[:,0:2], "\n  u std:", np.std(u))
	# Final calculations
	error = np.linalg.norm(u - u2)
	fpc = _fp_coeff(u)

	return cntr, u, u0, d, jm, p, fpc
