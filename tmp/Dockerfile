FROM python:3.13-alpine AS build-stage
RUN apk add build-base libffi-dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir wheel
RUN pip wheel --no-cache-dir -r requirements.txt -w ./wheels
FROM python:3.13-alpine AS runtime-stage
WORKDIR /app
COPY --from=build-stage /app/wheels ./wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=./wheels -r requirements.txt
RUN rm -rf ./wheels requirements.txt
COPY main.py .
RUN mkdir /logs
VOLUME /logs
RUN adduser -D appuser
RUN addgroup appuser_group
RUN addgroup appuser appuser_group
RUN chown -R :appuser_group /logs
RUN chmod -R g+rwX /logs
RUN su - appuser
EXPOSE 8080
ENTRYPOINT ["python", "main.py"]
