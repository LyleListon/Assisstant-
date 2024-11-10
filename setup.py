from setuptools import setup, find_packages

setup(
    name="personal_assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "types-selenium==3.141.9",
        "webdriver_manager>=3.8.0",
        "typing-extensions>=4.0.0",
        "mypy>=1.0.0",
        "pytest>=7.0.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
    ],
    python_requires=">=3.8",
)
