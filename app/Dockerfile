FROM python:3.10.13-bookworm
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow
RUN apt-get clean && apt-get update && apt-get install -y \
    bash \
    wget \
    fswatch \
    tzdata \
    nano \
    curl \
    iputils-ping \
    inotify-tools

RUN apt-get install -y \
    orthanc-wsi

RUN sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
COPY . .
RUN chmod +x ./*.sh
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && rm requirements.txt