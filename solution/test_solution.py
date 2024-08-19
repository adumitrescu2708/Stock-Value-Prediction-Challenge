'''
    Copyright: Dumitrescu Alexandra - Jan 2024
'''
import unittest
import os
import datetime
import pandas as pd
import solution

# Directory with stock exchange datasets
DATASET_DIR_NAME = "stock_price_data_files"

# Directory for resulted predictions
RESULTS_DIR_NAME = "predict_price_data_files"

class TestSolution(unittest.TestCase):
    '''
        This is a class used for unittesting
    '''
    def setUp(self):
        self.num_files = 2  # This value can be varied for further testing purposes
        self.result = solution.collect_consecutive_stock_values(self.num_files)
        solution.predict_stock_values(self.num_files)

    def test_collect_consecutive_stock_values(self):
        '''
            Unit test for testing 1st function collect_consecutive_stock_values
        '''
        stock_id_processed = {}
        for dataset in self.result:
            stock_id = dataset['stock'].iloc[-1]
            stock_id_processed[stock_id] = True

        # This checks that the correct number of files have been processed
        for directory in os.listdir(DATASET_DIR_NAME):
            counter_files_processed_per_directory = 0
            counter_total_files = len(os.listdir(os.path.join(DATASET_DIR_NAME, directory)))
            counter_expected_process = min(counter_total_files, self.num_files)

            for file in os.listdir(os.path.join(DATASET_DIR_NAME, directory)):
                filename = file.split(".")[0]
                if filename in stock_id_processed:
                    counter_files_processed_per_directory += 1
            self.assertEqual(counter_expected_process, \
                counter_files_processed_per_directory, "Incorect number of processed files")

        # This checks that the resulted datasets have no more than 10 values
        for dataset in self.result:
            self.assertGreaterEqual(10, dataset.shape[0])

        # This checks that the resulted datasets contain consecutive results
        # Note that: 'consecutive' in terms of datetime
        for dataset in self.result:
            self.assertTrue(dataset['date'].reset_index(drop=True)
                .equals(dataset.sort_values(by=['date'])['date'].reset_index(drop=True)), "yes")

    def test_predict_stock_values(self):
        '''
            Unit test for testing 2st function predict_stock_values
        '''
        resulted_datasets = []
        for dataset in os.listdir(RESULTS_DIR_NAME):
            resulted_dataset = pd.read_csv(os.path.join(RESULTS_DIR_NAME, dataset), header=None)
            resulted_dataset.columns = ["stock", "date", "price"]
            resulted_dataset["date"] = pd.to_datetime(resulted_dataset["date"])
            resulted_datasets.append(resulted_dataset)

        for dataset in resulted_datasets:
            second_highest_value = dataset[:-3]\
                .sort_values(by=['price'], ascending = False)\
                .reset_index(drop=True).iloc[1]["price"]

            n_th_stock_value    = dataset['price'].iloc[-4]
            n_1_th_stock_value  = dataset['price'].iloc[-3]
            n_2_th_stock_value  = dataset['price'].iloc[-2]
            n_3_th_stock_value  = dataset['price'].iloc[-1]

            # Check the first prediction's stock value is the second highest stock value in dataset
            self.assertEqual(second_highest_value, n_1_th_stock_value, \
                "First prediction should be equal to the second highest stock value in dataset")

            n_th_timestamp      = dataset['date'].iloc[-4]
            n_1_th_timestamp    = dataset['date'].iloc[-3]
            n_2_th_timestamp    = dataset['date'].iloc[-2]
            n_3_th_timestamp    = dataset['date'].iloc[-1]

            # Check the predicted timestamps to be consecutive
            timestamps = [n_th_timestamp, n_1_th_timestamp, n_2_th_timestamp, n_3_th_timestamp]
            for i in range(len(timestamps) - 1):
                self.assertEqual(timestamps[i] + datetime.timedelta(days = 1),\
                    timestamps[i + 1], "Predicted timestamps should be consecutive")

            # Check that the prediction calculus is applied correctly
            self.assertEqual(n_2_th_stock_value,  \
                round(n_1_th_stock_value + float(n_1_th_stock_value - n_th_stock_value) / 2, 2),\
                    "Wrong formula for 2nd prediction")

            self.assertEqual(n_3_th_stock_value,  \
                round(n_2_th_stock_value + float(n_2_th_stock_value - n_1_th_stock_value) / 4, 2),\
                    "Wrong formula for 3rd prediction")
