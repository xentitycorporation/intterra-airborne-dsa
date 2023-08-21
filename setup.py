from setuptools import find_packages, setup

setup(
    name="airborne_dsa",
    version="1.0",
    description="Data shipping app to support uploading files to Intterra airborne buckets",
    author="Intterra",
    author_email="devs@intterragroup.com",
    packages=find_packages(),  # same as name
    install_requires=[
        "boto3==1.28.26",
        "jsonschema==4.19.0",
        "watchdog==3.0.0",
    ],
)
