#  Predict next 3 values of Stock price (timeseries data)

> Name: *Dumitrescu Alexandra*  
> Date: *August 2024*

## Content
<ol>
  <li>Project Solution.</li>
  <li>Prediction logic.</li>
  <li>Run & UnitTesting command</li>
  <li>Other features</li>
  <li>Assumptions made. What can/should be done in the future?</li>
</ol>

## Project Solution.
One of the main **objectives** was to design an extensible, **scalable** solution with
**performance improvements**. My solution’s architecture is a microservices based one.
I used **Docker** for scalability and for posssible future improvements (connection to a NONSQL
time series database). I used Python, **Pandas**, **NumPY** for vectorized operations.
For unittesting I used Python **unittest** module.

## Prediction logic
The prediction logic is the one described in the tech challange.
Starting from last timestamp on day <n>, the function will append
the predictions for days <n + 1>, <n + 2>, <n + 3>.
For day <n + 1> the stock value will be the 2nd highest stock value from the 10
data points, for day <n + 2> it will be:

(1)     value <n + 2> = value<n + 1> + (value<n + 1> - value<n>)/2

For day <n + 3> the stock value will be:

(2)     value<n + 3> = value<n + 2> + (value<n + 2> - value<n + 1>)/4

Note: This can be improved in the future with AIML algorithms for further work

## Run commands
Command for running the service:
**docker-compose up --build**

Command for testing (Note that you should be in /solution directory):
**python3 -m unittest test_solution.py**

## Other features
I also implemented some unittests. More details can be found in the test class docstring.
Apart from that, the number of maximum files to be processed per stock exchange can be set
in .env file, along with a debug flag. The debug flag, if enabled, will log some relevant
information in the console. **NUM_FILES**, **DEBUG_DATA_FLOW**

## Assumptions made. What can/should be done in the future?
**Random date generator**: I assumed that the random date generated will guarantee that
10 values can be extracted from the dataset.

**Output format**: I assumed that the generated .csv file should be in chronological order

**Output removal on consecutive runs**: I assumed that on each consecutive run the previous results should be deleted.

**Output directory**: The solution should have the output directory created. A script can be added for creating it, if not existing
