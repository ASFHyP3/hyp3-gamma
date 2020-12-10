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
        'hyp3lib>=1.6.3,<2',
        'hyp3_metadata>=0.1.4,<1',
        'importlib_metadata',
        'numpy',
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
            'hyp3_gamma = hyp3_gamma.__main__:main',
            'rtc = hyp3_gamma.__main__:rtc',
            'check_coreg.py = hyp3_gamma.rtc.check_coreg:main',
            'rtc_sentinel.py = hyp3_gamma.rtc.rtc_sentinel:main',
            'smooth_dem_tiles.py = hyp3_gamma.rtc.smoothem:main',
        ]
    },

    zip_safe=False,
)
