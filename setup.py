from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cron-scanner',
    version='1.0.0',
    description='A tool to scan and analyze crontab entries within a specified time range',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tracey Russell',
    url='https://github.com/truss44/cron-scanner',
    packages=find_packages(),
    install_requires=[
        'pandas>=2.0.0',
        'openpyxl>=3.1.0',
        'reportlab>=4.0.0',
        'python-dateutil>=2.8.2',
        'croniter>=1.4.0',
        'cron-descriptor>=1.4.3',
    ],
    entry_points={
        'console_scripts': [
            'cron-scanner=cron_scanner.scanner:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
)
