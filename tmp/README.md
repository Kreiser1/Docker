# Конспект по Docker
## Dockerfile
Dockerfile - файл с инструкциями для постройки образа Docker.  
Команды Dockerfile:  
```Dockerfile
FROM - образ, на основе которого создаётся новый.
FROM python:3.13
RUN - выполнить команду при постройке образа.
RUN apt install build-essential
COPY - копировать файлы с хоста на образ.
COPY . .
COPY main.py .
ADD - распаковка архивов и скачивание из Интернета.
ADD https://example.com/file.txt .
WORKDIR - рабочая папка (рекомендуется /app)
WORKDIR /app
ENV - задать переменную среды.
ENV APP_VERSION=1.0
ARG - задать переменную среды, но на этапе сборки.
ARG TARGET_ARCH=x86_64
EXPOSE - открыть порт
EXPOSE 8080
CMD - команда по умолчанию на этапе выполнения.
CMD ["python", "main.py"]
ENTRYPOINT - точка входа, в отличие от CMD, всегда выполняется.
ENTRYPOINT ["nginx"]
Также можно использовать CMD как продолжение, которое можно переопределить:
ENTRYPOINT ["python"]
CMD ["main.py"]
USER - переключиться на другого пользователя Linux.
USER appuser
```
## Тегирование
У образов есть теги. По умолчанию это название:latest, но можно его переопределить.  
docker build -t container-name:tag .  
Можно давать тег версиями типа v1.0 или, например, container:development, container:production.  
## Контекст сборки
В образ попадают файлы из образа FROM, а также скопированные через COPY.  
## Слои и кеширование
Образ нужно писать в 2 стадии - build и runtime. В build нужно построить всё для runtime, используя тяжёлые компиляторы, а в runtime - использовать slim-версии и построенное в build, тогда образ выйдет легковесным.  
## Multi-stage build
Это практика написания Dockerfile, в которой используют несколько стадий. К примеру:  
```Dockerfile
FROM python:3.13-slim AS build-time
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir wheel
RUN pip wheel --no-cache-dir -r requirements.txt -w ./wheels
FROM python:3.13-slim AS run-time
WORKDIR /app
COPY --from=build-time /app/wheels ./wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=./wheels -r requirements.txt
RUN rm -rf ./wheels requirements.txt
COPY main.py .
ENTRYPOINT ["python", "main.py"]
```
Здесь мы скачали и скомпилировали зависимости на тяжёлом образе, а установили их и запустили на лёгком, который получился в итоге.  
## Best practices
Использовать multi-stage build.  
Использовать легковесные дистрибутивы типа -slim и -alpine.  
Писать .dockerignore.  
Располагать команды от редко-меняющихся к часто-меняющимся сверху вниз.  
Связывать команды RUN через && и \.  
Никогда не запускать от имени root. Создавать отдельного пользователя.  
Не использовать latest потому, что он часто меняется.  
Не оставлять токены, пароли и приватные ключи в образе.  
Использовать COPY вместо ADD, когда не нужна распаковка или скачивание.  
Один процесс - один контейнер.  
Использовать JSON-синтаксис в ENTRYPOINT и CMD для PID 1.
Добавить HEALTHCHECK для того, чтобы удостовериться, что образ работает исправно.
## Команды
```bash
docker build - постройка образа.
docker images - образы.
docker pull - скачивание образа.
docker push - добавление образа в реестр.
docker tag - дать тег образу.
docker history - история.
docker run - запустить образ.
docker ps - перечислить запущенные контейнеры.
docker stop - остановить контейнер.
docker logs - логи.
docker exec - ???
docker network - ???
```
## Docker compose
docker-compose.yml - файл, где описаны несколько контейнером в декларативном стиле на YAML. Например: приложение + база данных + nginx.
