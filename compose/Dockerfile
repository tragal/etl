FROM registry.access.redhat.com/ubi9/python-39

WORKDIR /opt/app-root/src/

# Build as root (required for native deps)
USER root

RUN dnf install -y \
    gcc \
    python3-devel \
    postgresql-devel \
    unzip \
    && dnf clean all

COPY pyproject.toml poetry.lock* ./

#RUN pip install --no-cache-dir poetry \
#    && poetry config virtualenvs.create true \
#    && poetry install --no-interaction --no-ansi --no-root

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root

ENV VIRTUAL_ENV=/opt/app-root/src/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY etl/ etl/

USER root
RUN chown -R 1001:1001 /opt/app-root/src/ \
    && chmod -R +x /opt/app-root/src/
USER 1001

# ENTRYPOINT ["python", "-m", "etl.cli"]
# CMD ["run"]
CMD ["bash"]
