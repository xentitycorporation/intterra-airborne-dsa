from setuptools import find_packages, setup

setup(
    name="airborne_dsa",
    version="1.0",
    description="Data shipping app to support uploading files to Intterra airborne buckets",
    author="Intterra",
    author_email="devs@intterragroup.com",
    packages=find_packages(),  # same as name
    install_requires=[
        "boto3",
        "jsonschema",
        "watchdog",
    ],
)
