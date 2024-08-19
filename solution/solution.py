'''
    Copyright: Dumitrescu Alexandra - Jan 2024
'''
import sys
import os.path
import datetime
import logging
import random
import pandas as pd

# Global logger
logger = logging.getLogger()

# Directory with stock exchange datasets
DATASET_DIR_NAME    = "stock_price_data_files"

# Directory for resulted predictions
RESULTS_DIR_NAME    = "predict_price_data_files"

# Debug flag - active if the DEBUG_DATA_FLOW env variable is set, logging messages are printed
DEBUG_ENABLE        = os.environ.get("DEBUG_DATA_FLOW") == "true"


def collect_consecutive_stock_values(max_files_nr):
    '''
        1st API function 
        
        - Each directory in the DATASET_DIR_NAME directoy marks a Stock Exchange.
        For each stack exchange found in the DATASET_DIR_NAME directoy, the function
        processes maximum max_files_nr .csv files.
        
        - For each dataset, the function generates a random date.
        Note: The date was generated randomly between the lowest date and the 10th
        greatest date, in order to properly guarantee that 10 consecutive values
        from any random date can be retrieved. This could be improved in the feature
        
        - For each dataset, starting from the generated random date, returns
        a dataset holding the next consecutive 10 values, sorted by timestamp
        Note: 'Consecutive' in the terms of timestamp
    '''

    # Check if the directory of stack exchanges exists and if it is a directory
    if not os.path.exists(DATASET_DIR_NAME) or not os.path.isdir(DATASET_DIR_NAME):
        print("Cannot find datasets directory!")
        sys.exit(-1)

    consecutive_stock_values = []

    # List available stock exchange directories
    for directory in os.listdir(DATASET_DIR_NAME):
        # Count processed datasets per stock exchange
        inspected_files_per_directory = 0
        # List avilable datasets
        for file in os.listdir(os.path.join(DATASET_DIR_NAME, directory)):
            # Check to be a proper file entry
            if not os.path.isfile(os.path.join(DATASET_DIR_NAME, directory, file)):
                continue

            inspected_files_per_directory += 1
            # Get the dataset from the .csv file
            dataset = pd.read_csv(os.path.join(DATASET_DIR_NAME, directory, file), header=None)

            # Return an info log if the dataset is empty
            if dataset.empty:
                if DEBUG_ENABLE:
                    logger.info("Found empty dataset in %s", file)
                continue

            # Assuming that 10 values should be returned
            if dataset.shape[0] < 10:
                if DEBUG_ENABLE:
                    logger.info("Insufficient data in dataset %s", file)
                continue
            
            dataset.columns = ["stock", "date", "price"]

            # Assume that all values are for the same stock
            if not (dataset['stock'] == dataset['stock'].iloc[0]).all():
                if DEBUG_ENABLE:
                    logger.info("Invalid stock id found %s", file)
                continue                

            # Convert the date entry into a Datetime
            dataset["date"] = pd.to_datetime(dataset["date"], dayfirst=True)

            # Sort the entries cronologically by date
            dataset.sort_values(by=['date'], inplace=True)

            # Generate a random date between the lowest and 10th highest date
            earliest_datetime = dataset["date"].iloc[0]
            latest_datetime = dataset["date"].iloc[-10]
            random_datetime = earliest_datetime + \
            datetime.timedelta(days=random.randint(0, (latest_datetime - earliest_datetime).days))

            # Log the generated random date
            if DEBUG_ENABLE:
                logger.info("Generated random date %s for %s", random_datetime, file)

            # Return from the starting date the resulted 10 cronological entries
            consecutive_stock_values.append(dataset[dataset["date"] > random_datetime].iloc[: 10])

            # Stop when reaching the input number of files
            if inspected_files_per_directory == int(max_files_nr):
                break

        # Log if the stock exchange directory didn't have any valid dataset
        if inspected_files_per_directory == 0:
            if DEBUG_ENABLE:
                logger.info("Unable to find any .csv file in %s", directory)

    return consecutive_stock_values


def predict_stock_values(max_files_nr):
    '''
        2nd API function 

        - Retrieves the list of processed datasets resulted from 1st API.

        - The prediction logic is the one described in the tech challange.
        Starting from last timestamp on day <n>, the function will append
        the predictions for days <n + 1>, <n + 2>, <n + 3>. For day <n + 1>
        the stock value will be the 2nd highest stock value from the 10
        data points, for day <n + 2> it will be:
        (1)     value<n + 1> + (value<n + 1> - value<n>)/2
        For day <n + 3> the stock value will be:
        (2)     value<n + 2> + (value<n + 2> - value<n + 1>)/4
        Note: This can be improved in the future with AIML algorithms
        
        - The resulted dataset, after appending the 3 predicitons will be
        printed in the RESULTS_DIR_NAME directory.
        Note: We considered that the 1st column, <stock_id> will be the name
        of the resulted dataset.
    '''

    # Collect datasets
    stock_values = collect_consecutive_stock_values(max_files_nr)

    # Remove previous dataset results, if existant
    if os.path.exists(RESULTS_DIR_NAME):
        for file in os.listdir(RESULTS_DIR_NAME):
            os.remove(os.path.join(RESULTS_DIR_NAME, file))

    for dataset in stock_values:
        # Collect the timestamp and the value for nth entry
        n_th_timestamp      = dataset["date"].iloc[-1]
        n_th_stock_value    = dataset["price"].iloc[-1]

        # Create an auxiliar dataset, holding the entries sorted
        # descending by stock value
        dataset_sorted_by_stock_value = \
            dataset.sort_values(by=['price'], ascending=False).reset_index(drop=True)

        # Collect the 2nd highest stock value. It will be the prediction for day <n + 1>
        n_1_th_stock_value = dataset_sorted_by_stock_value["price"].iloc[1]
        n_1_timestamp = n_th_timestamp + datetime.timedelta(days = 1)

        # Compute prediction for day <n + 2>, as explained in formula (1)
        n_2_th_stock_value = round(n_1_th_stock_value + \
            float(n_1_th_stock_value - n_th_stock_value) / 2, 2)
        n_2_th_timestamp = n_th_timestamp + datetime.timedelta(days = 2)

        # Compute prediction for day <n + 3>, as explained in formula (2)
        n_3_th_stock_value = round(n_2_th_stock_value + \
            float(n_2_th_stock_value - n_1_th_stock_value) / 4, 2)
        n_3_th_timestamp = n_th_timestamp + datetime.timedelta(days = 3)

        # Append the prediction entries to the output dataset
        new_data = [
            [dataset["stock"].iloc[-1], n_1_timestamp, n_1_th_stock_value],
            [dataset["stock"].iloc[-1], n_2_th_timestamp, n_2_th_stock_value],
            [dataset["stock"].iloc[-1], n_3_th_timestamp, n_3_th_stock_value]
        ]

        new_rows = pd.DataFrame(new_data, columns = ["stock", "date", "price"])
        dataset = pd.concat([dataset, new_rows], ignore_index=True)

        # Print predicted values
        if DEBUG_ENABLE:
            logger.info("Predicted %s, %s, %s for the stock %s",\
                n_1_th_stock_value, n_2_th_stock_value, n_3_th_stock_value, \
                dataset["stock"].iloc[-1])

        dataset.to_csv(os.path.join(RESULTS_DIR_NAME, str(dataset["stock"].iloc[-1]) + \
            ".csv"), header = False, index = False)


def setup_logger():
    '''
        Function that sets up a logger.
        If env variable DEBUG_DATA_FLOW is enabled, then debug info is printed
    '''

    # create a stream handler and set the level to INFO in avoid printing all debug messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # set the time format
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)

    # logging messages will be output to INFO level
    logger.setLevel(logging.INFO)
    logger.addHandler(ch)

if __name__ == "__main__":
    # The maximum number of files that will be processed must be sent as an argument
    if len(sys.argv) != 2:
        print("Bad format! Please try: solution.py <files_nr>")
        sys.exit(-1)

    # Setup logger. Logging messages have debug purposes and will be present
    # if the environment variable DEBUG_DATA_FLOW is set
    setup_logger()

    files_nr = sys.argv[1]

    predict_stock_values(files_nr)
