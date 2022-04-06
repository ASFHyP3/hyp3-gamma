from pathlib import Path

from setuptools import find_packages, setup

readme = Path(__file__).parent / 'README.md'

setup(
    name='hyp3_gamma',
    use_scm_version=True,
    description='HyP3 plugin for SAR processing with GAMMA',
    long_description=readme.read_text(),
    long_description_content_type='text/markdown',

    url='https://github.com/ASFHyP3/hyp3-gamma',
    project_urls={
        'Documentation': 'https://hyp3-docs.asf.alaska.edu',
    },

    author='ASF APD/Tools Team',
    author_email='uaf-asf-apd@alaska.edu',

    license='BSD',
    include_package_data=True,

    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],

    python_requires='~=3.8',

    install_requires=[
        'gdal',
        'geopandas',
        'hyp3lib>=1.7.0,<2',
        'importlib_metadata',
        'jinja2',
        'lxml',
        'numpy>=1.17,<1.18',
        'pillow',
        'python-dateutil',
    ],

    extras_require={
        'develop': [
            'flake8',
            'flake8-import-order',
            'flake8-blind-except',
            'flake8-builtins',
            'pytest',
            'pytest-cov',
            'pytest-console-scripts',
        ]
    },

    packages=find_packages(),

    entry_points={'console_scripts': [
            'hyp3_gamma = hyp3_gamma.__main__:main',
            'rtc = hyp3_gamma.__main__:rtc',
            'rtc_sentinel.py = hyp3_gamma.rtc.rtc_sentinel:main',
            'insar = hyp3_gamma.__main__:insar',
            'ifm_sentinel.py = hyp3_gamma.insar.ifm_sentinel:main',
            'interf_pwr_s1_lt_tops_proc.py = hyp3_gamma.insar.interf_pwr_s1_lt_tops_proc:main',
            'unwrapping_geocoding.py = hyp3_gamma.insar.unwrapping_geocoding:main',
            'water_map = hyp3_gamma.__main__:water_map',
            'flood_map = hyp3_gamma.__main__:flood_map',
        ]
    },

    zip_safe=False,
)
