from setuptools import setup, find_packages

setup(
    name="voice-assistant-workers",
    version="1.0.0",
    description="Celery background workers for voice assistant",
    packages=find_packages(),
    python_requires=">=3.11",
)
