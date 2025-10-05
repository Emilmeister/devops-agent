FROM python:3.13

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY litellm_patch/lite_llm_patch.py /usr/local/lib/python3.13/site-packages/google/adk/models/lite_llm.py

COPY a2a_patch/telemetry.py /usr/local/lib/python3.13/site-packages/a2a/utils/telemetry.py

COPY worker_agent worker_agent

COPY prompts.yaml prompts.yaml

CMD python -m worker_agent.start_a2a

