FROM python:3.11-slim-bookworm
ARG BLENDER_VERSION=4.5.15
RUN apt-get update && apt-get install -y --no-install-recommends curl xz-utils libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libegl1 libsm6 libxkbcommon0 libgomp1 && rm -rf /var/lib/apt/lists/*
RUN curl --fail --location "https://download.blender.org/release/Blender4.5/blender-${BLENDER_VERSION}-linux-x64.tar.xz" -o /tmp/blender.tar.xz && mkdir /opt/blender && tar -xJf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 && rm /tmp/blender.tar.xz
ENV BLENDER_BIN=/opt/blender/blender
WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "tasks.py", "doctor"]
