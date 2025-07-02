FROM public.ecr.aws/lambda/python:3.11

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY  creds.py main.py lambda_function.py ${LAMBDA_TASK_ROOT}
COPY creds.py main.py lambda_function.py ${LAMBDA_TASK_ROOT}
COPY companies/ ${LAMBDA_TASK_ROOT}/companies/
COPY helper/ ${LAMBDA_TASK_ROOT}/helper/
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]
