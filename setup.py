# minimal setup.py so pip install -e works
from setuptools import setup

setup(

    entry_points={
        'console_scripts': ['dbt-ai = dbt_ai.main:main']
    }
)
