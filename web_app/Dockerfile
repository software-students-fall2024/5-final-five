# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-xetex \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port used by Gunicorn
EXPOSE 8080

# Set the default command to run Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:create_app()"]
