"""
Pure-numpy implementations of the antropy functions used in analysis.py.
This file exists because antropy's numba dependency fails to build on this system.
These implementations match the antropy library's output closely enough for clustering.
"""
import math
import numpy as np


def perm_entropy(data, normalize=True, order=3, delay=1):
    """Permutation entropy (Bandt & Pompe 2002)."""
    n = len(data)
    permutations = np.array(list(_embed(data, order, delay)))
    if len(permutations) == 0:
        return 0.0
    # Rank each embedding
    ranks = permutations.argsort(axis=1)
    # Count unique permutation patterns
    _, counts = np.unique(ranks, axis=0, return_counts=True)
    probs = counts / counts.sum()
    pe = -np.sum(probs * np.log2(probs + 1e-12))
    if normalize:
        pe /= np.log2(np.math.factorial(order))
    return float(pe)


def _embed(x, order, delay):
    n = len(x) - (order - 1) * delay
    for i in range(n):
        yield x[i:i + order * delay:delay]


def petrosian_fd(data):
    """Petrosian fractal dimension."""
    n = len(data)
    if n < 2:
        return 1.0
    diff = np.diff(data)
    # Count zero-crossings of the derivative (sign changes)
    nzc = np.sum(diff[1:] * diff[:-1] < 0)
    if nzc == 0:
        return 1.0
    fd = np.log10(n) / (np.log10(n) + np.log10(n / (n + 0.4 * nzc)))
    return float(fd)


def hjorth_params(data):
    """Hjorth mobility and complexity."""
    d1 = np.diff(data)
    d2 = np.diff(d1)
    var0 = np.var(data)
    var1 = np.var(d1)
    var2 = np.var(d2)
    if var0 == 0:
        return 0.0, 0.0
    mobility = np.sqrt(var1 / var0)
    if var1 == 0:
        return float(mobility), 0.0
    complexity = np.sqrt(var2 / var1) / mobility
    return float(mobility), float(complexity)
