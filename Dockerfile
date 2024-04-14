FROM ubuntu:22.04

WORKDIR ./ResultAthle/

# Install Python
RUN apt-get -y update && \
    apt-get install -y python3-pip

# Install project dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY test.py .
COPY utils ./utils
COPY src ./src
COPY main.ipynb .
CMD ["python3", "test.py"]