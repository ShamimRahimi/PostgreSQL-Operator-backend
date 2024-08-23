FROM hub.hamdocker.ir/python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /code/


# Expose port
EXPOSE 8000

# # Run the application
CMD ["gunicorn", "--bind", ":8000", "django_project.wsgi:application"]
