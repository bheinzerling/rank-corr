import numpy as np

def pair_is_concordant(o1, o2):
	return (o1[0] > o2[0] and o1[1] > o2[1]) or (o1[0] < o2[0] and o1[1] < o2[1])

def pair_is_disconcordant(o1, o2):
	return (o1[0] > o2[0] and o1[1] < o2[1]) or (o1[0] < o2[0] and o1[1] > o2[1])

def tau(values1, values2, get_pairs=False):
	""" Computes Kendall's tau rank correlation coefficient for two	lists of observations with no ties
		
		Parameters:
			values1:	list of observations
			values2:	list of observations
			get_pairs:	set True to return the number of concordant and discordant pairs instead of tau
	"""
	concordant_pairs = 0
	discordant_pairs = 0
	zipped_vals = list(zip(values1, values2))
	for i, o1 in enumerate(zipped_vals):
		for o2 in zipped_vals[i+1:]:
			if pair_is_concordant(o1, o2):
				concordant_pairs += 1
			if pair_is_disconcordant(o1, o2):
				discordant_pairs += 1
	
	n = len(zipped_vals)
	tau = float(concordant_pairs - discordant_pairs) / (0.5 * n * (n - 1))
	if get_pairs:
		return (concordant_pairs, discordant_pairs)
	else:
		return tau

def rho(values1, values2):
	""" Computes Spearman's rho for two lists of observations with no ties

		Parameters:
			values1:	list of observations
			values2:	list of observations
	"""
	v1, v2 = np.array(values1), np.array(values2)
	n = len(v1)
	return 1 - 6 * np.sum((v1 - v2)**2) / float(n * (n*n -1))

def AP(gold_ranking, test_ranking):
	""" Computes the average precision of a test ranking, given a gold standard ranking

		Parameters:
			gold_ranking:	gold standard ranking as list
			test_ranking:	test ranking as list
	"""
	# notation follows Kishida (2005)
	test = np.array(test_ranking)
	gold = np.array(gold_ranking)
	n = len(test)
	R = len(gold)

	x_i = np.zeros(n)
	x_i[np.where(test == gold)] = 1
	I_i = np.zeros(n)
	I_i[np.where(x_i != 0)] = 1

	# p(m) is the precision up to rank m 
	p = lambda m: 1.0 / m * np.sum(x_i[:m])
	p_i = np.array([p(m) for m in range(1, n+1)])

	return 1.0 / R * I_i.dot(p_i)

if __name__ == '__main__':
	a = [1,2,3,4,5,6,7,8,9]
	b = [1,2,3,4,5,6,7,8,9]
	print(AP(a, b))
	print(GAP(a, b))
