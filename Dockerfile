FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code



RUN pip install --upgrade pip
#RUN pip install ultralytics==8.0.20
RUN pip install ultralytics==8.1

RUN apt-get update && apt-get install -y libgl1-mesa-glx

COPY ./PIPE_model/requirements.txt /code/
RUN pip install -r requirements.txt


COPY ./PIPE_model /code/

EXPOSE 5000

#CMD ["python", "app.py"]
CMD ["gunicorn", "-w" ,"2", "-b", ":5000 ","wsgi:app"]