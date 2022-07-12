from typing import Union, Optional
import numpy as np
import cvxpy as cp

from portfolio_optimization.meta import *
from portfolio_optimization.utils import *

__all__ = ['mean_cvar']


def mean_cvar(expected_returns: np.ndarray,
              returns: np.ndarray,
              weight_bounds: Union[tuple[np.ndarray, np.ndarray],
                                   tuple[Optional[float], Optional[float]]],
              investment_type: InvestmentType,
              population_size: int,
              beta: float = 0.95) -> np.array:
    """
    Optimization along the mean-CVaR frontier (conditional drawdown-at-risk).

    :param expected_returns: expected returns for each asset.
    :type expected_returns: np.ndarray of shape(Number of Assets)

    :param returns: historic returns for all your assets
    :type returns: np.ndarray of shape(Number of Assets, Number of Observations)

    :param beta: var confidence level (expected var on the worst (1-beta)% days)
    :type beta: float

    :param weight_bounds: minimum and maximum weight of each asset OR single min/max pair if all identical.
                            No short selling --> (0, None)
    :type weight_bounds: tuple OR tuple list, optional

    :param investment_type: investment type (fully invested, market neutral, unconstrained)
    :type investment_type: InvestmentType

    :param population_size: number of pareto optimal portfolio weights to compute along the efficient frontier
    :type population_size: int

    :return the portfolio weights that are in the efficient frontier

    """
    assets_number, observations_number = returns.shape

    # Variables
    w = cp.Variable(assets_number)
    alpha = cp.Variable()
    u = cp.Variable(observations_number)

    # Parameters
    target_cvar = cp.Parameter(nonneg=True)

    # Objectives
    portfolio_return = expected_returns.T @ w
    objective = cp.Maximize(portfolio_return)

    # Constraints
    portfolio_cvar = alpha + 1.0 / (observations_number * (1 - beta)) * cp.sum(u)
    lower_bounds, upper_bounds = get_lower_and_upper_bounds(weight_bounds=weight_bounds,
                                                            assets_number=assets_number)
    constraints = [portfolio_cvar <= target_cvar,
                   returns.T @ w + alpha + u >= 0,
                   u >= 0,
                   w >= lower_bounds,
                   w <= upper_bounds]
    investment_target = get_investment_target(investment_type=investment_type)
    if investment_target is not None:
        constraints.append(cp.sum(w) == investment_target)

    # Problem
    problem = cp.Problem(objective, constraints)

    # Solve for different volatilities
    weights = get_optimization_weights(problem=problem,
                                       variable=w,
                                       parameter=target_cvar,
                                       parameter_array=np.logspace(-3.5, -0.5, num=population_size))

    return weights