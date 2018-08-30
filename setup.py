from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='qci-api',
    version='0.1.1',
    packages=['qci'],
    url='https://github.com/Etaoni/qci-api',
    license='MIT License',
    author='Alex Lin',
    author_email='alexwllin@gmail.com',
    description='A Python interface for Qiagen Clinical Insight\'s REST API',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
