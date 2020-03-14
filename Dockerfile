FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /proj_code
WORKDIR /proj_code
COPY requirements.txt /proj_code/
RUN pip install -r requirements.txt
COPY . /proj_code/
