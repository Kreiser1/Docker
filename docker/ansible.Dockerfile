FROM python:3.13-slim-bookworm
RUN pip install --no-cache-dir ansible-core==2.19.14
WORKDIR /work
ENTRYPOINT ["ansible-playbook", "-i", "localhost,", "-c", "local"]
