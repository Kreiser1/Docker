# K2-02: save your completed file as lab/Dockerfile.
# 1. Use the same Python base as docker/bootstrap.Dockerfile.
# 2. Set /app as WORKDIR and unbuffered Python output.
# 3. Copy app.py and index.html from the build context.
# 4. Prepare /data and give UID/GID 10001 access to it.
# 5. Set USER, document port 8000 and run app.py with Python.
# 6. Add LABEL course.student with your student code (no full name).

FROM python:3.13-slim
LABEL course.student="080808"
WORKDIR /app
COPY . .
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
EXPOSE 8000
CMD ["python", "app.py"]