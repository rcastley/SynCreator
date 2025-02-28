from setuptools import find_packages, setup

setup(
    name="flaskr",
    version="3.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "requests", "waitress"],
)
