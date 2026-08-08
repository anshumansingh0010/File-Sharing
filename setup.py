from setuptools import setup, find_packages

setup(
    name="file-sharing",
    version="1.0.0",
    description="GTK 4 / Libadwaita Local Network File Sharing Application",
    author="Anshuman",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "frontend": ["style.css"],
    },
    py_modules=["main"],
    install_requires=[
        "psutil",
        "PyGObject",
    ],
    entry_points={
        "console_scripts": [
            "file-sharing=main:main",
        ],
    },
)
