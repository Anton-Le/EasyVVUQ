"""Analysis element for Markov Chain Monte Carlo (MCMC).
"""
import chaospy as cp
import pandas as pd
from .base import BaseAnalysisElement
from .results import AnalysisResults


class MCMCAnalysisResults(AnalysisResults):
    """The analysis results class for MCMC.

    Parameters
    ----------
    samples: ndarray of shape (nsamples, ndim)
    qoi: ndarray of shape (nsamples, 1)
    """

    def __init__(self, chains):
        self.chains = chains

    def plot_hist(self, input_parameter, chain, skip=0):
        import matplotlib.pyplot as plt
        plt.hist(self.chains[chain][input_parameter].iloc[skip:], 20)

    def plot_chain(self, input_parameter, chain=None):
        import matplotlib.pyplot as plt
        if chain is None:
            for chain in self.chains:
                plt.plot(self.chains[chain][input_parameter])
        else:
            plt.plot(self.chains[chain][input_parameter])


class MCMCAnalysis(BaseAnalysisElement):
    """The analysis part of the MCMC method in EasyVVUQ

    Parameters
    ----------
    sampler: MCMCSampler
       an instance of MCMCSampler used to generate MCMC samples
    qoi: str
       name of the qoi
    """

    def __init__(self, sampler, qoi=None):
        self.sampler = sampler
        self.qoi = qoi

    def element_name(self):
        """Name for this element"""
        return "MCMCAnalysis"

    def element_version(self):
        """Version of this element"""
        return "0.1"

    def analyse(self, df):
        chains = dict([(chain_id, []) for chain_id in df[('chain_id', 0)].unique()])
        for chain in chains:
            chain_values = df[df[('chain_id', 0)] == chain]
            values = chain_values.groupby(('iteration', 0)).apply(lambda x: x.mean())
            indexes = values.index.values
            for a, b in zip(indexes[:-1], indexes[1:]):
                chains[chain] += [values.loc[a][self.sampler.inputs].to_dict()] * (b - a)
        for chain in chains:
            tmp = dict([(input_, []) for input_ in chains[chain][0]])
            for row in chains[chain]:
                for input_ in chains[chain][0]:
                    tmp[input_].append(row[input_])
            chains[chain] = pd.DataFrame(tmp)
        return MCMCAnalysisResults(chains)
