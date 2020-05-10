"""Apitist package"""
from pkg_resources import DistributionNotFound, get_distribution

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "apitist"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound as e:
    __version__ = "unknown"
    print(e)
finally:
    del get_distribution, DistributionNotFound
