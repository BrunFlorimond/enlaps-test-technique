FROM public.ecr.aws/amazonlinux/amazonlinux:2023
# Use Amazon Linux 2023 as the base image

# Install necessary build dependencies for Python 3.13
# Start of Selection
RUN dnf -y install gcc openssl-devel bzip2-devel libffi-devel zlib-devel git unzip tar rsync
# End of Selection

# Download and build Python 3.13 from source
RUN curl -O https://www.python.org/ftp/python/3.13.2/Python-3.13.2.tgz \
    && tar -xzf Python-3.13.2.tgz \
    && cd Python-3.13.2 \
    && ./configure --enable-optimizations \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.13.2 Python-3.13.2.tgz

# Ensure Python 3.13 is the default version
RUN alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.13 1

# Install pip for Python 3.13
RUN curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3.13 get-pip.py \
    && rm -f get-pip.py

# Set up the application directory
WORKDIR /app/python-env

# Create a Python virtual environment using Python 3.13
RUN python3.13 -m venv python3.13

# Activate the virtual environment
RUN chmod +x /app/python-env/python3.13/bin/activate

WORKDIR /app

# Install AWS CLI
RUN curl --retry 5 "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

# Upgrade pip inside the virtual environment
RUN /app/python-env/python3.13/bin/pip install --upgrade pip




