from setuptools import setup

setup(
    name="cci-ftp-scan",
    version='0.1.0',
    description='ESA CCI FTP Scanner',
    license='GPL 3',
    author='Norman Fomferra',
    packages=['cciftp'],
    entry_points={
        'console_scripts': [
            'cci-ftp-scan = cciftp.scan:main'
        ]
    }
)
