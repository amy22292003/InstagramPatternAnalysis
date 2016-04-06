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

	# calculating u_c
	u_c = u_old / u_old.sum(axis=1)[:,None]
	um_c = u_c ** m

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	d1 = 0
	if data1 is not None:
		data1 = data1.T
		cntr1 = um.dot(data1) / (np.ones((data1.shape[1],
										1)).dot(np.atleast_2d(um.sum(axis=1))).T)
		d1 = _distance(data1, cntr1)
		max1 = np.amax(d1)
		d1 = d1 / max1

	# data2
	d2 = 0
	if similarity2 is not None:
		#transform um(the sum of a location's all cluster membership = 1) to (the sum of a cluster's all location membership = 1)

		print("similarity2", similarity2[0:5,0])

		d2 = um_c.dot(similarity2)
		max2 = np.amax(d2)
		print("d2.shape", d2.shape)
		print("b4-- d1:", d1[0:5,0],d1[0:5,1], " \n  ,d2:", d2[0:5,0],d2[0:5,1])
		d2 = d2 / max2
	
	# combined distance and similarity of two data
	d = w * d1 + (1-w) * (1-d2)
	print("-- d1:", d1[0:6,0],d1[0:6,1], " \n  ,d2:", d2[0:6,0],d2[0:6,1],d2[0:6,2], " \n  ,d:", d[0:5,0],d[0:5,1])
	print("   std 1:", np.std(d1), " ,2:", np.std(d2), " ,d:", np.std(d))

	d = np.fmax(d, np.finfo(np.float64).eps)

	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	print("end u.sum:", u.sum(axis=0), u.sum(axis=1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	print("end u.sum:", u.sum(axis=0), u.sum(axis=1))
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
	um_c = u_c ** m

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	d1 = 0
	if data1 is not None:
		data1 = data1.T
		cntr1 = um.dot(data1) / (np.ones((data1.shape[1],
										1)).dot(np.atleast_2d(um.sum(axis=1))).T)
		d1 = _distance(data1, cntr1)
		max1 = np.amax(d1)
		d1 = d1 / max1

	# data2
	d2 = 0
	if similarity2 is not None:
		# remain the belonging rate >= the k-th max location of each cluster in um_c
		filter_k = lambda row:row < sorted(row, reverse=True)[k-1]
		fail_indices = np.apply_along_axis(filter_k, axis=1, arr=um_c)
		um_c[fail_indices] = 0
		#um_c[~fail_indices] = 1

		d2 = um_c.dot(similarity2)
		max2 = np.amax(d2)
		print("b4-- d1:", d1[0:3,0],d1[0:3,1], " \n  ,d2:", d2[0:4,0],d2[0:4,1])
		#print("   std 1:", np.std(d1), " ,2:", np.std(d2))
		d2 = d2 / max2
	
	# combined distance and similarity of two data
	d = w * d1 + (1-w) * (1-d2)
	print("-- d1:", d1[0:5,0],d1[0:5,1], " \n  ,d2:", d2[0:5,0],d2[0:5,1], " \n  ,d:", d[0:5,0],d[0:5,1])
	print("   std 1:", np.std(d1), " ,2:", np.std(d2), " ,d:", np.std(d))

	d = np.fmax(d, np.finfo(np.float64).eps)

	jm = (um * d ** 2).sum()

	u = d ** (- 2. / (m - 1))
	u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))
	return cntr1, u, jm, d1, d2, d

def _cmeans0_lfreq(data1, similarity2, u_old, c, w, m, *para):
	"""
	Single step in generic fuzzy c-means clustering algorithm.
	data2 is for intersect counting
	"""
	# parameters
	k = para[0]
	user_count = para[1]

	# Normalizing, then eliminating any potential zero values.
	u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
	u_old = np.fmax(u_old, np.finfo(np.float64).eps)

	um = u_old ** m

	# calculating u_c
	u_c = u_old / u_old.sum(axis=1)[:,None]
	um_c = u_c ** m

	# Calculate cluster centers
	# data1:2861,2; um:30,2861
	d1 = 0
	if data1 is not None:
		data1 = data1.T
		cntr1 = um.dot(data1) / (np.ones((data1.shape[1],
										1)).dot(np.atleast_2d(um.sum(axis=1))).T)
		d1 = _distance(data1, cntr1)
		max1 = np.amax(d1)
		d1 = d1 / max1

	# data2
	d2 = 0
	if similarity2 is not None:
		# remain the belonging rate >= the k-th max location of each cluster in um_c
		filter_k = lambda row:row < sorted(row, reverse=True)[k-1]
		fail_indices = np.apply_along_axis(filter_k, axis=1, arr=um_c)
		um_c[fail_indices] = 0
		#um_c[~fail_indices] = 1
		#print("um_c:", sum(um_c[0,:]))

		print("similarity2:", similarity2[0:4,0])
		similarity = np.apply_along_axis(lambda col:col * user_count / sum(user_count), axis=0, arr=similarity2)
		print("similarity:", similarity[0:4,0], similarity[0:4,1])

		d2 = um_c.dot(similarity)

		max2 = np.amax(d2)
		print("b4-- d1:", d1[0:3,0],d1[0:3,1], " \n  ,d2:", d2[0:4,0],d2[0:4,1])
		#print("   std 1:", np.std(d1), " ,2:", np.std(d2))
		d2 = d2 / max2
	
	# combined distance and similarity of two data
	d = w * d1 + (1-w) * (1-d2)
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
		print(p, "----------------------------")
		u2 = u.copy()
		[cntr1, u, Jjm, d1, d2, d] = _cmeans0(data1, similarity2, u2, c, w, m, *para)
		jm = np.hstack((jm, Jjm))
		p += 1

		# Stopping rule
		if np.linalg.norm(u - u2) < error:
			break

	print("Fin u>>\n", u[:,0],u[:,1], u[:,2], "\nu std:", np.std(u))
	# Final calculations
	error = np.linalg.norm(u - u2)
	fpc = _fp_coeff(u)

	return cntr1, u, u0, d1, d2, d, jm, p, fpc
