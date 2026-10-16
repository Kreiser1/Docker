# Подготовка кабинета

Выполнить до занятия под обычной студенческой учётной записью. Студентам не нужны права установки. Наличие Docker ещё не доказывает доступность Linux-движка, Compose и сети.

Из корня курса:

```text
docker version
docker compose version
docker info --format '{{.OSType}}'
docker build -f docker/bootstrap.Dockerfile -t devops-course:base lab
docker build -f docker/tools.Dockerfile -t devops-course-tools:base .
docker build -f docker/ansible.Dockerfile -t devops-course-ansible:base .
docker compose --profile registry --profile monitoring pull registry prometheus grafana
docker compose config
docker compose up -d
docker compose run --rm tools ps -ef
docker compose run --rm tools ss -lnt
docker compose run --rm ansible demo.yml
docker compose run --rm ansible demo.yml
```

Второй Ansible запуск — changed=0. Проверьте создание заявки, остановку API, HTTP 503, восстановление и сохранность данных. Запустите мониторинг, обе цели должны быть UP. Проверьте создание и экспорт панели через анонимную роль Editor в Grafana. Доступ анонимный только для локального учебного стенда: порты привязаны к 127.0.0.1; не публикуйте такой стенд в интернет.

На один ПК рассчитана одна рабочая папка и один студент/пара за раз. Для общего Docker-host потребуются отдельные имена проектов, порты и изоляция студентов. Не переносите конфигурацию на общий сервер без адаптации.

При плохой сети заранее сохраните подготовленные образы через docker image save и перенесите их через учебную папку, затем docker image load. Версии Linux/архитектуры должны быть совместимы. Архивы в GitHub не загружать. Registry только локальный, без реальных секретов.

GitHub проверяется отдельно: fork, PR в собственную копию, Actions и доступ преподавателя. Образец сдачи должен пройти весь цикл. При отсутствии Git работает браузерный маршрут. При отсутствии интернета фиксируйте локальный результат и принимайте загрузку позже.

Не требуйте от студентов установки Ansible/Python: они находятся в контейнерах. Контейнер tools разделяет PID/network только с api учебного проекта; привилегированный контейнер, Docker socket и host PID не используются. Ansible изменяет только учебный том.

Перед потоком зафиксируйте digests используемых образов и прогоните полный маршрут на самом слабом ПК. Указанные теги фиксируют версию/ветку, но могут обновляться; не являются неизменяемым digest-lock.
