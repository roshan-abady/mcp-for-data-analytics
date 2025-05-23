from setuptools import setup, find_packages

setup(
    name="time-mcp-server",
    version="0.1.0",
    description="Time MCP Server with timezone utilities",
    author="MCP Developer",
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",
        "pydantic>=2.5.0",
        "pytz>=2023.3",
        "python-dateutil>=2.8.2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
