# Конспект по Docker
# Dockerfile
Dockerfile - файл с инструкциями для постройки образа Docker.  
Команды Dockerfile:  
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
ENV - зада  
