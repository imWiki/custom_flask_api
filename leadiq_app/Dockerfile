FROM python:2.7-slim
MAINTAINER Vignesh Meyyappan <informvicky@gmail.com>
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python app.py
