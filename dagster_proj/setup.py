from setuptools import find_packages, setup

setup(
    name="dagster_proj",
    packages=find_packages(exclude=["dagster_proj_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={
    "dev": [
        "dagit", 
        "pytest", 
        "pandas", 
        "sodapy",
        "google-cloud-storage",
        'google-cloud-bigquery',
        'google-auth',
        'pandas-gbq'
        ]
    },
)
