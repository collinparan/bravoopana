FROM python:3.11.1-buster

WORKDIR /front_end
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
COPY ./ ./
RUN chmod u+x etl.py 

ENTRYPOINT ["python","etl.py"]

EXPOSE 80
