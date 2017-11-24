# coding: utf-8
from __future__ import unicode_literals

import logging
import os
import pickle
import time
import random
from concurrent import futures

from trajectory.sim_run import sim_run_func

logger = logging.getLogger(__name__)


class SimGenerator(object):
    """generate simulate data"""

    def __init__(
        self, train_stocks, model_name, explore_rate, episode_length, model_dir='./models',
        data_dir='./sim_data', debug=False, worker_num=4, sim_count=2500, rounds_per_step=1000,
        worker_timeout=300,
    ):
        self._model_name = model_name
        self._model_dir = model_dir
        self._episode_length = episode_length
        self._explore_rate = explore_rate
        self._train_stocks = train_stocks
        self._data_dir = data_dir
        self._sim_count = sim_count
        self._rounds_per_step = rounds_per_step
        self._worker_num = worker_num
        self._worker_timeout = worker_timeout
        self._debug = debug

    def _get_sim_file_path(self, data_dir):
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        file_name = '{mn}.{ts}.pkl'.format(mn=self._model_name, ts=int(time.time()))
        return os.path.join(data_dir, file_name)

    def run(self, sim_batch_size=100):
        current_count = 0
        with futures.ProcessPoolExecutor(max_workers=self._worker_num) as executor:
            while current_count < self._sim_count:
                future_to_idx = dict((executor.submit(sim_run_func, {
                    'stock_name': random.choice(self._train_stocks),
                    'episode_length': self._episode_length,
                    'rounds_per_step': self._rounds_per_step,
                    'model_name': self._model_name,
                    'model_dir': self._model_dir,
                    'model_feature_num': 5,
                    'sim_explore_rate': self._explore_rate,
                    'debug': self._debug,
                }), current_count + i) for i in range(sim_batch_size))
                _results = []
                for future in futures.as_completed(future_to_idx, timeout=self._worker_timeout):
                    idx = future_to_idx[future]
                    exception = future.exception(timeout=self._worker_timeout)
                    if exception:
                        logger.error('Sim[{i}] error: {e}'.format(i=idx, e=exception))
                        continue
                    logger.info('Sim[{i}] finished'.format(i=idx))
                    _results.append(future.result(timeout=self._worker_timeout))
                if _results:
                    # save results to file
                    file_path = self._get_sim_file_path(self._data_dir)
                    with open(file_path, 'w') as f:
                        pickle.dump(_results, f)
                current_count += sim_batch_size