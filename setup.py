from typing import List
from setuptools import setup, find_packages

VERSION = {}
with open("mallennlp/version.py", "r") as version_file:
    exec(version_file.read(), VERSION)


def read_reqs_file(path: str) -> List[str]:
    reqs: List[str] = []
    with open(path, "r") as reqs_file:
        for line in reqs_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            reqs.append(line)
    return reqs


setup(
    name="allennlp-manager",
    version=VERSION["VERSION"],
    description="Your manager for AllenNLP experiments",
    url="https://github.com/epwalsh/allennlp-manager",
    packages=find_packages(exclude=["mallennlp.tests*"]),
    install_requires=read_reqs_file("requirements.txt"),
    tests_require=read_reqs_file("requirements.dev.txt"),
    python_requires=">=3.6.1,<3.7.0",
    include_package_data=True,
)
