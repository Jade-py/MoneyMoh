FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

EXPOSE 8000

# Copy the script
COPY . .

# Set the environment variables
ENV BOT_TOKEN=$BOT_TOKEN
ENV DEBUG=$DEBUG
ENV SECRET_KEY=$SECRET_KEY
ENV MYSQL_NAME=$MYSQL_NAME
ENV MYSQL_HOST=$MYSQL_HOST
ENV MYSQL_PASSWORD=$MYSQL_PASSWORD
ENV MYSQL_PORT=$MYSQL_PORT
ENV MYSQL_USER=$MYSQL_USER
ENV TEST_DATABASE_NAME=$TEST_DATABASE_NAME


# Run the script when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["python", "bot.py"]
