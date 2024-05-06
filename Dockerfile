FROM python:3.9-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update  && \
    pip install --upgrade pip setuptools wheel && \
    apt-get install ffmpeg libsm6 libxext6 -y && \
    apt install -y python3-dev \
    libhdf5-dev \
    python3-h5py \
    libboost-mpi-python-dev \
    musl-dev \
    libpq-dev postgresql postgresql-contrib

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]