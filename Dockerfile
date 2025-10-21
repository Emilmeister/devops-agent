FROM python:3.13

WORKDIR /app

COPY pyproject.toml pyproject.toml

RUN pip install poetry \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi

COPY litellm_patch/lite_llm_patch.py /usr/local/lib/python3.13/site-packages/google/adk/models/lite_llm.py

COPY a2a_patch/telemetry.py /usr/local/lib/python3.13/site-packages/a2a/utils/telemetry.py

COPY worker_agent worker_agent

COPY prompts.yaml prompts.yaml

ENV PATH="/app/.venv/bin:$PATH"

CMD python -m worker_agent.start_a2a

