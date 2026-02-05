FROM registry.access.redhat.com/ubi9/python-39

# WORKDIR /opt/app-root/src/
RUN printf 'Current directory: %s\n' "$(pwd)"
RUN printf 'Contents of %s:\n' "$(pwd)" && ls -la

# Build as root (required for native deps)
USER root

# Copy the package source and install the project into the in-project venv
COPY src/ ./

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
 && python -m pip install --no-cache-dir -e .

RUN chown -R 1001:1001 ./ && chmod -R +x ./
USER 1001

# ENTRYPOINT ["python", "-m", "etl.cli"]
# CMD ["run"]
# CMD ["bash"]
