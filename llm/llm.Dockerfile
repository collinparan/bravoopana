FROM python:3.11.1-buster

WORKDIR /llm_assistant
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
COPY ./ ./
RUN chmod u+x llm.py 

ENTRYPOINT ["python","llm.py"]

EXPOSE 81
