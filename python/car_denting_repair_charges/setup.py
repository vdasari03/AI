from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="car_denting_repair_charges",
    version="1.0.0",
    author="Insurance AI Team",
    description="Image-driven car damage assessment and cost estimation application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/car_denting_repair_charges",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pillow>=10.0.0",
        "opencv-python>=4.8.0.76",
        "numpy>=1.24.3",
        "openai>=0.27.8",
        "anthropic>=0.7.1",
        "requests>=2.31.0",
        "pydantic>=2.3.0",
    ],
)
