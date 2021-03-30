from pathlib import Path

from setuptools import find_packages, setup

readme = Path(__file__).parent / 'README.md'

setup(
    name='hyp3_metadata',
    use_scm_version=True,
    description="Package for generating HyP3 products' metadata",
    long_description=readme.read_text(),
    long_description_content_type='text/markdown',

    url='https://github.com/ASFHyP3/hyp3-metadata-templates',

    author='ASF APD/Tools Team',
    author_email='uaf-asf-apd@alaska.edu',

    license='BSD',
    include_package_data=True,

    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    python_requires='~=3.6',

    install_requires=[
        'importlib_metadata',
        'jinja2',
        'gdal',
        'pillow',
        'python-dateutil',
    ],

    extras_require={
        'develop': [
            'pytest',
            'pytest-cov',
        ]
    },

    packages=find_packages(),

    zip_safe=False,
)
