# Define custom function directory
ARG FUNCTION_DIR="/function"
FROM --platform=$TARGETPLATFORM python:3.12 AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

WORKDIR ${FUNCTION_DIR}
COPY requirements.txt .

# Install the function's dependencies
RUN pip install --target ${FUNCTION_DIR} -r requirements.txt

COPY lambda_function.py .
# COPY .env . # Do not copy .env file to image for security reasons

FROM --platform=$TARGETPLATFORM python:3.12-slim


ARG FUNCTION_DIR

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y wkhtmltopdf

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "lambda_function.handler" ]
