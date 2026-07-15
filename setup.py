from setuptools import setup, find_packages

setup(
    name="QueryDoc",
    version="1.0.0",
    author="Hit Lathiya",
    author_email="lathiyahit2005@gmail.com",
    description="A personalized AI-powered voice assistant with ultra-low latency, built using FastAPI, Flask, Qdrant, Deepgram, and Groq. It supports Retrieval-Augmented Generation (RAG) through both text and voice interfaces.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LathiyaHit/QueryDoc",
    packages=find_packages(),
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "voice-api=services.api.main:app",
        ],
    },
)
