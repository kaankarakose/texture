FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# Install Python, pip, and other dependencies
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install python3.10-venv -y

# Optionally, create a virtual environment (if you prefer to use one)
RUN python3 -m venv /env
ENV PATH="/env/bin:$PATH"
ENV HF_HOME="/cache"
EXPOSE 8186

# Install Python packages
RUN pip3 install --no-cache-dir diffusers torch numpy accelerate wheel setuptools flask transformers
RUN pip install -U flash-attn --no-build-
RUN pip install -U xformers --index-url https://download.pytorch.org/whl/cu124

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . /app

# Set default command to keep container running
# ENTRYPOINT [ "python3" ]

# # Command to run the application
# CMD [ "llm_server.py" ]

CMD ["/bin/bash"]