"""
cmeans.py : Fuzzy C-means clustering algorithm.
"""
import numpy as np
import sys
from scipy.spatial.distance import cdist

# data1:coordinate; similarity2:tag intersect similarity
def _cmeans0_ori(data1, similarity2, u_old, c, w, m, *para):
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
	d1 = 0
	if data1 is not None:
		data1 = data1.T
		cntr1 = um.dot(data1) / (np.ones((data1.shape[1],
										1)).dot(np.atleast_2d(um.sum(axis=1))).T)
		d1 = _distance(data1, cntr1) # euclidean distance
		d1 = d1 / np.std(d1)

	# data2
	d2 = 0
	if similarity2 is not None:
		d2 = um.dot(1 - similarity2) / np.ones((similarity2.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T
		d2 = d2 / np.std(d2)
	
	# combined distance and similarity of two data
	d = w * d1 + (1-w) * d2

	d = np.fmax(d, np.finfo(np.float64).eps)
	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return cntr1, u, jm, d1, d2, d

# data1:coordinate; similarity2:tag intersect similarity
def _cmeans0_kth(data1, similarity2, u_old, c, w, m, *para):
	"""
	Single step in generic fuzzy c-means clustering algorithm.
	data2 is for intersect counting
	"""
	k = para[0]

	# Normalizing, then eliminating any potential zero values.
	u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	u_old = np.fmax(u_old, np.finfo(np.float64).eps)

	um = u_old ** m

	# calculating u_c
	u_c = u_old / u_old.sum(axis=1)[:,None]

	# remain the belonging rate >= the k-th max location of each cluster in um_c
	filter_k = lambda row:row < sorted(row, reverse=True)[k-1]
	fail_indices = np.apply_along_axis(filter_k, axis=1, arr=u_c)
	um[fail_indices] = 0

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	d1 = 0
	if data1 is not None:
		data1 = data1.T
		cntr1 = um.dot(data1) / (np.ones((data1.shape[1],
										1)).dot(np.atleast_2d(um.sum(axis=1))).T)
		d1 = _distance(data1, cntr1) # euclidean distance
		#print("b4-- d1:", d1[0:5,0],d1[0:5,1])
		#print("  min d1:", np.min(d1), ";max d1:", np.max(d1), "   std 1:", np.std(d1))
		d1 = d1 / np.std(d1)

	# data2
	d2 = 0
	if similarity2 is not None:
		#print("similarity2", similarity2[0:5,0])
		#d2 = um_c.dot(similarity2)
		d2 = um.dot(1 - similarity2) / np.ones((similarity2.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T
		#print("b4--d2:", d2[0:5,0],d2[0:5,1])
		#print("  d2.shape", d2.shape, ",std2:", np.std(d2))
		d2 = d2 / np.std(d2)
	
	# combined distance and similarity of two data
	d = w * d1 + (1-w) * d2
	#print("-- d1:", d1[0:6,0],d1[0:6,1], " \n  ,d2:", d2[0:6,0],d2[0:6,1],d2[0:6,2], " \n  ,d:", d[0:5,0],d[0:5,1])
	#print("  min d1:", np.min(d1), ";max d1:", np.max(d1), ",max d2:", np.max(d2))
	#print("   std 1:", np.std(d1), " ,2:", np.std(d2), " ,d:", np.std(d))

	d = np.fmax(d, np.finfo(np.float64).eps)

	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	#print("end u.sum:", u.sum(axis=0), u.sum(axis=1), "\nu[:,0]:", u[:,0])
	#print("/:", np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0))))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	#print("end u.sum:", u.sum(axis=0), u.sum(axis=1), "\nu:", u[:,0])
	return cntr1, u, jm, d1, d2, d

def _cmeans0_lfreq(data1, similarity2, u_old, c, w, m, *para):
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
	u_c = u_old / u_old.sum(axis=1)[:,None]

	# remain the belonging rate >= the k-th max location of each cluster in um_c
	filter_k = lambda row:row < sorted(row, reverse=True)[k-1]
	fail_indices = np.apply_along_axis(filter_k, axis=1, arr=u_c)
	um[fail_indices] = 0

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	d1 = 0
	if data1 is not None:
		data1 = data1.T
		cntr1 = um.dot(data1) / (np.ones((data1.shape[1],
										1)).dot(np.atleast_2d(um.sum(axis=1))).T)
		d1 = _distance(data1, cntr1) # euclidean distance
		#print("b4-- d1:", d1[0:5,0],d1[0:5,1])
		#print("  min d1:", np.min(d1), ";max d1:", np.max(d1), "   std 1:", np.std(d1))
		d1 = d1 / np.std(d1)

	# data2
	d2 = 0
	if similarity2 is not None:
		#print("similarity2", similarity2[0:5,0])
		print("similarity2.sum(0):", similarity2.sum(axis=0)[0:5], "\tsimilarity2.max:", np.amax(similarity2))
		inverse_similarity = (1 - similarity2) / np.ones((similarity2.shape[0], 1)).dot(np.atleast_2d(location_frequency)).T
		print("inverse_similarity", inverse_similarity[0:3,0:3], ",max:", np.amax(inverse_similarity))
		print(" /.shape:", np.ones((similarity2.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T.shape, np.ones((similarity2.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T[0:5,0:3])
		print("um.sum:", um.sum(axis=1)[0:5], um.sum(axis=0)[0:3])
		d2 = um.dot(1-similarity2) / np.ones((similarity2.shape[1],1)).dot(np.atleast_2d(um.sum(axis=1))).T
		print("b4--d2:", d2[0:5,0],d2[0:5,1])
		print("  d2.shape", d2.shape, ",std2:", np.std(d2))
		d2 = d2 / np.std(d2)
	
	# combined distance and similarity of two data
	d = w * d1 + (1-w) * d2
	print("-- d1:", d1[0:5,0],d1[0:5,1], " \n  ,d2:", d2[0:5,0],d2[0:5,1], " \n  ,d:", d[0:5,0],d[0:5,1])
	print("   std 1:", np.std(d1), " ,2:", np.std(d2), " ,d:", np.std(d))

	d = np.fmax(d, np.finfo(np.float64).eps)

	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return cntr1, u, jm, d1, d2, d

def _distance(data, centers):
	return cdist(data, centers).T


def _fp_coeff(u):
	n = u.shape[1]

	return np.trace(u.dot(u.T)) / float(n)

def cmeans(data1, similarity2, c, w, m, error, maxiter, algorithm, *para):
	"""
	data2 is for intersect counting
	"""
	init = None
	seed = None
	# Setup u0
	if init is None:
		if seed is not None:
			np.random.seed(seed=seed)
		n = data1.shape[1]
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
	elif algorithm is "kthCluster":
		_cmeans0 = _cmeans0_kth
	elif algorithm is "kthCluster_LocationFrequency":
		_cmeans0 = _cmeans0_lfreq
	else:
		print("Error, nonexistent fuzzy c means algorithm:", algorithm)
		sys.exit()

	# Main cmeans loop
	while p < maxiter - 1:
		print(p, "---------------------------->")
		u2 = u.copy()
		[cntr1, u, Jjm, d1, d2, d] = _cmeans0(data1, similarity2, u2, c, w, m, *para)
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

	return cntr1, u, u0, d1, d2, d, jm, p, fpc
