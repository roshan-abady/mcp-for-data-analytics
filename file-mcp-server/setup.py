from setuptools import setup, find_packages

setup(
    name="file-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",
        "python-magic>=0.4.27",
        "gitignore-parser>=0.0.9",
        "pathspec>=0.11.0",
        "watchdog>=3.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "pylint>=2.13.0",
            "mypy>=0.940",
        ],
    },
    entry_points={
        "console_scripts": [
            "file-mcp-server=server.main:main",
        ],
    },
    author="MCP for Data Analytics Team",
    author_email="your-email@example.com",
    description="An MCP server providing secure, read-only access to files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/file-mcp-server",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
)
