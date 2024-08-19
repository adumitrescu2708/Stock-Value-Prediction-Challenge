FROM python:3.9

# set working directory
WORKDIR /solution

# upgrade pip
RUN pip install --upgrade pip

# install requirements
COPY requirements.txt /solution
RUN pip install -r requirements.txt

# copy required sources
COPY . /solution

# command to run server
CMD python solution.py $NUM_FILES