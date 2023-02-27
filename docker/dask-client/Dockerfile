FROM python:3.9

RUN pip install dask-gateway==2023.1.1 numpy==1.24.1 cloudpickle==2.2.0 pandas==1.5.2
COPY . /src/
WORKDIR /src/

CMD ["bash", "-c", "sleep infinity"]

