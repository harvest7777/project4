FROM python:3.13-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY node.py .
EXPOSE 5000
CMD ["uv", "run", "python", "node.py"]
