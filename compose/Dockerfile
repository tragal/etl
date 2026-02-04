FROM registry.access.redhat.com/ubi9/python-39

WORKDIR /opt/app-root/src/

# Build as root (required for native deps)
USER root

#RUN dnf install -y \
#    gcc \
#    python3-devel \
#    postgresql-devel \
#    unzip \
#    && dnf clean all

COPY pyproject.toml poetry.lock* ./

# Install poetry and configure an in-project virtualenv
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the package source and install the project into the in-project venv
COPY etl/ /opt/app-root/src/etl/
RUN poetry install --no-interaction --no-ansi

#ENV VIRTUAL_ENV=/opt/app-root/src/.venv
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"


USER root
RUN chown -R 1001:1001 /opt/app-root/src/ \
    && chmod -R +x /opt/app-root/src/
USER 1001

# ENTRYPOINT ["python", "-m", "etl.cli"]
# CMD ["run"]
CMD ["bash"]
