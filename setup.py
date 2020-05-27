from setuptools import setup, find_packages

setup(
    name='workorder',
    version=1.0,
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "xlwings>=0.19.4",
        "pyodbc>=4.0.30",
        "prodctrlcore @ git+https://github.com/paddymills/prodctrlcore#egg=prodctrlcore-0.1"
    ]
)
