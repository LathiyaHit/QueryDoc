from setuptools import setup, find_packages

setup(
    name="voice-assistant-api",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="FastAPI backend service for the AI voice assistant",
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests*", "alembic*"]),
    install_requires=[
        line.strip()
        for line in open("../../requirements.txt")
        if line.strip() and not line.startswith("#") and not line.startswith("-r")
    ],
    extras_require={
        "dev": [
            line.strip()
            for line in open("../../requirements-dev.txt")
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]
    },
)
