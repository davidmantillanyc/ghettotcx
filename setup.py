from setuptools import setup, find_packages
setup(
        version='0.2.dev0',
        name="ghettotcx",
        package_dir={'ghettotcx': 'ghettotcx'},
        packages=find_packages(),
        install_requires=[
            'pandas',
            'numpy',
            'matplotlib',
            ],
        extras_require = {
            }
        )
