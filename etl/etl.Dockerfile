FROM python:3.10-buster

WORKDIR /etl
COPY ./etl/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
COPY ./etl ./
RUN chmod u+x etl.py 

ENTRYPOINT ["python","etl.py"]

EXPOSE 80
