import numpy as np
import datetime as dt

from portfolio_optimization.meta import *
from portfolio_optimization.utils.metrics import *
from portfolio_optimization.utils.tools import *
from portfolio_optimization.assets import *
from portfolio_optimization.portfolio import *
from portfolio_optimization.paths import *
from portfolio_optimization.bloomberg.loader import *


def test_multi_period_portfolio():
    prices = load_prices(file=TEST_PRICES_PATH)

    N = 10
    periods = [(dt.date(2017, 1, 1), dt.date(2017, 3, 1)),
               (dt.date(2017, 3, 15), dt.date(2017, 5, 1)),
               (dt.date(2017, 5, 1), dt.date(2017, 8, 1))]

    multi_period_portfolio = MultiPeriodPortfolio()
    returns = np.array([])
    for i, period in enumerate(periods):
        assets = Assets(prices=prices, start_date=period[0], end_date=period[1])
        weights = rand_weights(n=assets.asset_nb, zeros=assets.asset_nb - N)
        portfolio = Portfolio(weights=weights, assets=assets, pid=str(i))
        multi_period_portfolio.add(portfolio)
        returns = np.concatenate([returns, portfolio_returns(assets.returns, weights)])

    assert np.all((returns - multi_period_portfolio.returns) < 1e-10)
    assert abs(returns.mean() - multi_period_portfolio.mean) < 1e-10
    assert abs(returns.std(ddof=1) - multi_period_portfolio.std) < 1e-10
    assert abs(np.sqrt(np.sum(np.minimum(0, returns - returns.mean()) ** 2) / (len(returns) - 1))
               - multi_period_portfolio.downside_std) < 1e-10
    assert abs(multi_period_portfolio.annualized_mean / multi_period_portfolio.annualized_std
               - multi_period_portfolio.sharpe_ratio) < 1e-10
    assert abs(multi_period_portfolio.annualized_mean / multi_period_portfolio.annualized_downside_std
               - multi_period_portfolio.sortino_ratio) < 1e-10
    assert max_drawdown_slow(multi_period_portfolio.prices_compounded) == multi_period_portfolio.max_drawdown
    assert np.array_equal(multi_period_portfolio.fitness,
                          np.array([multi_period_portfolio.mean, -multi_period_portfolio.std]))
    multi_period_portfolio.reset_fitness(fitness_type=FitnessType.MEAN_DOWNSIDE_STD)
    assert np.array_equal(multi_period_portfolio.fitness,
                          np.array([multi_period_portfolio.mean, -multi_period_portfolio.downside_std]))
    multi_period_portfolio.reset_fitness(fitness_type=FitnessType.MEAN_DOWNSIDE_STD_MAX_DRAWDOWN)
    assert np.array_equal(multi_period_portfolio.fitness,
                          np.array([multi_period_portfolio.mean,
                                    -multi_period_portfolio.downside_std,
                                    -multi_period_portfolio.max_drawdown]))
    assert len(multi_period_portfolio.assets_index) == len(periods)
    assert len(multi_period_portfolio.assets_names) == len(periods)
    assert multi_period_portfolio.composition.shape[1] == len(periods)
    multi_period_portfolio.reset_metrics()
    assert multi_period_portfolio._mean is None
    assert multi_period_portfolio._std is None
    multi_period_portfolio.plot_rolling_sharpe(days=20)