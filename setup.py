from setuptools import setup, find_packages

setup(
    name='workorder',
    version=1.0,
    description="Workorder automation script",
    install_requires=[
        "xlwings>=0.19.4",
        "pyodbc>=4.0.30",
        "prodctrlcore @ git+https://github.com/paddymills/prodctrlcore"
    ]
)
