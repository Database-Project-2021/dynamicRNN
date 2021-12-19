import time
import os
from typing import Callable

from scalablerunner.taskrunner import TaskRunner
from scalablerunner.adapter import DBRunnerAdapter
from cost_estimator import Loader

SERVER_COUNT = 1
DEST_DIR = '/opt/shared-disk2/sychou/dynamic_rnn/lock_overhead_exp2'

def get_temp_dir():
    # Create 'temp' directory
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    return temp_dir

def get_dataset_dir():
    # Create 'temp' directory
    temp_dir = 'dataset'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    return temp_dir

def config_db_runner_adapter(db_runner_adapter: DBRunnerAdapter) -> DBRunnerAdapter:
    db_runner_adapter.config(server_count=SERVER_COUNT, jar_dir='latest', sequencer="192.168.1.32", 
                             servers=["192.168.1.31", "192.168.1.30", "192.168.1.27", "192.168.1.26"], 
                            #  servers=["192.168.1.31"], 
                             clients=["192.168.1.9", "192.168.1.8"], 
                            #  clients=["192.168.1.9"], 
                             package_path='/home/db-under/sychou/autobench/package/jdk-8u211-linux-x64.tar.gz',
                             base_config='configs/lock_overhead_exp/bencher.toml')
    return db_runner_adapter

def naming(alts: dict):
    rte = alts['vanillabench']['org.vanilladb.bench.BenchmarkerParameters.NUM_RTES']
    return f'rte-{rte}'

def name_fn(reports_path: str, alts: dict):
    # rw = alts['elasqlbench']['org.elasql.bench.benchmarks.ycsb.ElasqlYcsbConstants.RW_TX_RATE']
    rw_dir = os.path.join(reports_path, naming(alts=alts))
    if not os.path.isdir(rw_dir):
        os.makedirs(rw_dir) 
    return rw_dir

def move2share_fn(reports_path: str, name_fn: Callable, alts: dict, base_config: str):
    dir_name = naming(alts=alts)
    src_path = name_fn(reports_path=reports_path, alts=alts)
    dest_dir = DEST_DIR
    dest_path = os.path.join(dest_dir, dir_name)

    os.system(f"rm -rf {dest_path}; mv {src_path} {dest_dir}")

def process_dataset():
    dest_path = DEST_DIR
    total_count = 3
    count = 0

    done_map = {}

    files = os.listdir(dest_path)
    while count < total_count:
        for f in files:
            fullpath = os.path.join(dest_path, f, 'reports')
            # if os.path.isfile(fullpath):
            #     print("File: ", f)
            if os.path.isdir(fullpath) and (not done_map.get(fullpath, False)):
                print("Folder: ", f)
                loader = Loader(f'{fullpath}', server_count=SERVER_COUNT, n_jobs=8)
                df_features = loader.load_features_as_df(auto_save=True)
                df_latencies = loader.load_latencies_as_df(auto_save=True)

                done_map[f'{fullpath}'] = True
                count += 1
        time.sleep(5)

if __name__ == '__main__':
    HOSTNAME = "140.114.85.15"
    USERNAME = "db-under"
    PASSWORD = "db-under"

    PORT = 22
    SSH_DEFAULT_RETRY_COUT = 3
    SSH_DEFAULT_CMD_RETRY_COUT = 2
    SSH_DEFAULT_IS_RAISE_ERR = False
    WORKSPACE_NAME = 'Lock_Overhead'

    dra = DBRunnerAdapter(reports_path=get_dataset_dir(), workspace=WORKSPACE_NAME)
    # Log file name
    dra.output_log(file_name='temp/total.log')
    # Connect to the remote host, where Auto-Bencher loactes
    dra.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD, port=PORT)
    dra = config_db_runner_adapter(dra)

    # Setting behaviors of the DBRunnerAdapter
    # Whether raise exception or not while error occur
    dra.set_default_is_raise_err(default_is_raise_err=SSH_DEFAULT_IS_RAISE_ERR)
    # The retrying count while the SSH connection fails
    dra.set_default_retry_count(default_retry_count=SSH_DEFAULT_RETRY_COUT)
    # The redoing count while the SSH command failed
    dra.set_default_cmd_retry_count(default_cmd_retry_count=SSH_DEFAULT_CMD_RETRY_COUT)


    ARGS_LOAD = {
                    # "elasqlbench": {
                    #     "org.elasql.bench.benchmarks.ycsb.ElasqlYcsbConstants.INIT_RECORD_PER_PART": "100000"
                    # }
                    "elasqlbench":
                    {
                        "org.elasql.bench.benchmarks.tpcc.ElasqlTpccConstants.WAREHOUSE_PER_PART": "5",
                    }
                }

    ARGS_BENCH = {
                    "vanillabench": {
                        "org.vanilladb.bench.BenchmarkerParameters.BENCHMARK_INTERVAL": "180000",
                    },
                    "elasql": {
                        "org.elasql.perf.tpart.TPartPerformanceManager.ENABLE_COLLECTING_DATA": "true"
                    },
                    "elasqlbench": {
                        "org.elasql.bench.benchmarks.tpcc.ElasqlTpccConstants.WAREHOUSE_PER_PART": "5",
                    #     "org.elasql.bench.benchmarks.ycsb.ElasqlYcsbConstants.INIT_RECORD_PER_PART": "100000",
                        # "org.elasql.bench.benchmarks.ycsb.ElasqlYcsbConstants.RW_TX_RATE": "1"
                    }
                }

    # Custom parameters
    # [Class, Parameter name, Value]
    PARAMS = [
        ["vanillabench", "org.vanilladb.bench.BenchmarkerParameters.NUM_RTES", "100"],
        ["vanillabench", "org.vanilladb.bench.BenchmarkerParameters.NUM_RTES", "130"],
        ["vanillabench", "org.vanilladb.bench.BenchmarkerParameters.NUM_RTES", "45"]
            ]

    # Base configurations
    LOAD_CONFIG = 'configs/lock_overhead_exp/load.toml'
    BENCH_CONFIG = 'configs/lock_overhead_exp/bench.toml'
    
    config_test = {
            f'Section Initialize': {
                'Group Initialize': {
                    'Call': dra.init_autobencher_load_test_bed,
                    'Param': {
                        'server_jar': ['jars/server.jar'], 
                        'client_jar': ['jars/client.jar'],
                        'alts': [ARGS_LOAD],
                        'base_config': [LOAD_CONFIG],
                        # An arbitrary name for the parameter that want to modify. You can give multiple custom parameters.
                        # 'custom_param1': PARAMS,
                    }
                },
            },
            f'Section Benchmark': {
                'Group Benchmark': {
                    'Call': dra.benchmark,
                    'Param': {
                        'name_fn': [name_fn],
                        'alts': [ARGS_BENCH],
                        'base_config': [BENCH_CONFIG],
                        # An arbitrary name for the parameter that want to modify. You can give multiple custom parameters.
                        'custom_param1': PARAMS,
                        'callback_fn': [move2share_fn],
                    }
                },
                'Group Process Dataset': {
                    'Call': process_dataset,
                },
            }
        }
    tr = TaskRunner(config=config_test)
    tr.run()