FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the script
COPY . .

# Set the environment variables
ENV BOT_TOKEN=$BOT_TOKEN


# Run the script when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["python", "bot.py"]
