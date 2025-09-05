"""Setup configuration for Subtitle Creator with Effects."""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A desktop application for creating stylized subtitle videos."

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove version comments and development dependencies
                    if 'pytest' not in line and 'black' not in line and 'flake8' not in line and 'pyinstaller' not in line:
                        requirements.append(line)
    return requirements

setup(
    name="subtitle-creator-with-effects",
    version="0.1.0",
    author="Subtitle Creator Team",
    author_email="team@subtitlecreator.com",
    description="A desktop application for creating stylized subtitle videos",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/subtitle-creator/subtitle-creator-with-effects",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "setuptools>=60.0.0",
            "wheel>=0.37.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "subtitle-creator=subtitle_creator.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "subtitle_creator": ["assets/*"],
    },
    zip_safe=False,
)