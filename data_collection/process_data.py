import os
import time

from cost_estimator import Loader

SERVER_COUNT = 1

def process_dataset():
    dest_path = '/opt/shared-disk2/sychou/dynamic_rnn/lock_overhead_exp'
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
    process_dataset()