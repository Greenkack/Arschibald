from setuptools import find_packages, setup

setup(
    name="demopythonpackage",
    version="0.1.0",
    description="DemoPythonPackage",
    author="KAI Agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
        ],
    },
)
