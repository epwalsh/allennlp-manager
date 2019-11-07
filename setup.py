from typing import List, Dict, Any
from setuptools import setup, find_packages

VERSION: Dict[str, Any] = {}
with open("mallennlp/version.py", "r") as version_file:
    exec(version_file.read(), VERSION)


def read_reqs_file(path: str) -> List[str]:
    reqs: List[str] = []
    with open(path, "r") as reqs_file:
        for line in reqs_file:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-e"):
                continue
            reqs.append(line)
    return reqs


setup(
    name="allennlp-manager",
    version=VERSION["VERSION"],
    description="Your manager for AllenNLP experiments",
    url="https://github.com/epwalsh/allennlp-manager",
    packages=find_packages(exclude=["mallennlp.tests*"]),
    package_data={"mallennlp": ["services/schema.sql", "assets/*.css"]},
    install_requires=read_reqs_file("requirements.txt") + ["allennlp"],
    tests_require=read_reqs_file("requirements.dev.txt"),
    python_requires=">=3.6.1,<3.8",
    include_package_data=True,
    entry_points={"console_scripts": ["mallennlp=mallennlp.bin.main:main"]},
)
