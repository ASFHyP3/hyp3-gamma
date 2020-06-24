import os

from setuptools import find_packages, setup

_HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(_HERE, 'README.md'), 'r') as f:
    long_desc = f.read()

setup(
    name='hyp3_rtc_gamma',
    use_scm_version=True,
    description='HyP3 plugin for radiometric terrain correction using GAMMA',
    long_description=long_desc,
    long_description_content_type='text/markdown',

    url='https://github.com/asfadmin/hyp3-rtc-gamma',

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
        'hyp3lib>=1.2.1,<2',
        'hyp3proclib~=1.0',
        'importlib_metadata',
        'lxml',
        'numpy',
        'scipy', 'requests', 'boto3', 'urllib3'
    ],

    extras_require={
        'develop': [
            'pytest',
            'pytest-cov',
            'pytest-console-scripts',
        ]
    },

    packages=find_packages(),

    entry_points={'console_scripts': [
            'rtc_gamma = hyp3_rtc_gamma.__main__:entry',
            'hyp3_rtc_gamma = hyp3_rtc_gamma.__main__:main',
            'hyp3_rtc_gamma_v2 = hyp3_rtc_gamma.__main__:main_v2',
            'check_coreg.py = hyp3_rtc_gamma.check_coreg:main',
            'rtc_sentinel.py = hyp3_rtc_gamma.rtc_sentinel:main',
            'smooth_dem_tiles.py = hyp3_rtc_gamma.smoothem:main',
            'xml2meta.py = hyp3_rtc_gamma.xml2meta:main',
        ]
    },

    zip_safe=False,
)
