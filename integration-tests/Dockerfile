FROM python:3.9-slim

WORKDIR /app
ARG PIP_EXTRA_INDEX_URL

# Install dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt

# Add the app
ADD . .

# Engage.
CMD ["behave", "--no-capture"]
