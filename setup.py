# minimal setup.py so pip install -e works
from setuptools import setup

setup(
    entry_points={
        "console_scripts": [
            "data-product-hub = data_product_hub.main:main",
            "dph = data_product_hub.main:main",
        ]
    }
)
