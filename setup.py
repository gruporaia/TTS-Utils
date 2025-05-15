from setuptools import setup, find_packages

setup(
    name="tts-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "num2words",
    ],
    author="RAIA - Rede de Avanço em Inteligência Artificial",
    description="Conjunto de ferramentas para processamento de áudio e texto em português para tarefas de Text-to-Speech (TTS)."
)