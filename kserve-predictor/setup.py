from setuptools import setup, find_packages

setup(
    name='bondmodel',
    version='0.9.0',
    author_email='diego.ciangottini@gmail.com',
    license='https://github.com/comp-dev-cms-ita/kserve-bond-server/blob/main/LICENSE',
    url='https://github.com/comp-dev-cms-ita/kserve-bond-serve',
    description='Model Server implementation for FPGA. \
                 Not intended for use outside KServe Frameworks Images',
    long_description=open('README.md').read(),
    python_requires='>3.7',
    packages=find_packages("bondmodel"),
    install_requires=[
        "kserve==0.9.0",
        "ray[serve]==1.10.0"
    ],
)
