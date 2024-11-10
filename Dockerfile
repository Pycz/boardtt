FROM ubuntu:24.04

ARG POETRY_VERSION=1.8

RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository multiverse  && \
    apt-get install -y tesseract-ocr libtesseract-dev python3 python3-pip fonts-ubuntu ttf-mscorefonts-installer pipx && \
    fc-cache -f -v && \
    pipx install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock /app/

ENV VENV_PATH=/app/.venv
ENV PATH="/root/.local/bin:$VENV_PATH/bin:${PATH}"

WORKDIR /app

ENV POETRY_NO_INTERACTION=1
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --verbose

COPY . /app

CMD ["python3", "-m", "examples.invisible_sun"]
#CMD ["python3"]
#CMD ["bash"]
