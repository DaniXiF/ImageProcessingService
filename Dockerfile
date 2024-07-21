FROM python:3.13.0b3-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./polybot ./polybot
ENTRYPOINT ["python", "-m"]
CMD ["polybot.app"]
