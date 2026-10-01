FROM python:3.12-slim-bookworm

RUN apt-get update \
	&& apt-get upgrade -y \
	&& rm -rf /var/lib/apt/lists/* \
	&& useradd --create-home --shell /bin/false appuser
WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER appuser
EXPOSE 5000
CMD ["python", "app.py"]