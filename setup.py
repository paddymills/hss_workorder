from setuptools import setup, find_packages

setup(
    name='hss_workorder',
    version=1.0,
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "xlwings>=0.19.4",
        "pyodbc>=4.0.30"
    ],
    dependency_links=[
        "git+https://github.com/paddymills/hss_core.git#egg=hss_core-0.1"
    ]
)
