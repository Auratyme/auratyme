FROM pytorch/pytorch:2.4.1-cuda11.8-cudnn9-runtime AS base

WORKDIR /app

RUN apt-get update

FROM base AS dev

RUN apt-get install curl -y

COPY microservices/schedules-ai/core/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader vader_lexicon

COPY libs/proto/schedules/v1/schedule_generation.proto /tmp/proto/

COPY microservices/schedules-ai/core . 

RUN mkdir -p /app/src/grpc_generated && \
    python -m grpc_tools.protoc \
    -I/tmp/proto \
    --python_out=/app/src/grpc_generated \
    --grpc_python_out=/app/src/grpc_generated \
    /tmp/proto/schedule_generation.proto 2>/dev/null || echo "Proto compilation done"

RUN sed -i 's/^import schedule_generation_pb2/from . import schedule_generation_pb2/' /app/src/grpc_generated/schedule_generation_pb2_grpc.py || true
RUN sed -i 's/^import schedule_generation_pb2/from . import schedule_generation_pb2/' /app/src/grpc_generated/schedule_generation_pb2_grpc.py || true

RUN echo '#!/bin/bash\n\n# Run scheduler in the background and redirect its output to a log file\npython3 -m src.core.scheduler > /app/scheduler.log 2>&1 &\n\n# Save scheduler PID\necho $! > /app/scheduler.pid\n\n# Wait 2 seconds for the scheduler to start\nsleep 2\n\n# Display the last 10 lines of the scheduler log\necho "Last lines of scheduler log:"\ntail -n 10 /app/scheduler.log\n\n# Run API server in foreground mode\necho "Starting API server..."\npython3 -m api.server\n' > /app/run.sh && chmod +x /app/run.sh

CMD ["/app/run.sh"]

FROM base AS prod

COPY microservices/schedules-ai/core/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader vader_lexicon

COPY libs/proto/schedules/v1/schedule_generation.proto /tmp/proto/

COPY microservices/schedules-ai/core .

RUN mkdir -p /app/src/grpc_generated && \
    python -m grpc_tools.protoc \
    -I/tmp/proto \
    --python_out=/app/src/grpc_generated \
    --grpc_python_out=/app/src/grpc_generated \
    /tmp/proto/schedule_generation.proto 2>/dev/null || echo "Proto compilation done"