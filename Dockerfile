FROM python:3.9

WORKDIR /

COPY . /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 5000
CMD ["python", "application.py"]
