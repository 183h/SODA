from setuptools import setup

setup(
    name='soda',
    version='0.1',
    author='Matej Puk',
    author_email='puk.matej@gmail.com',

    description='Simulator of distributed algorithms',
    url='https://github.com/mpuk/SODA',
    license='MIT',

    install_requires=[
        'Click',
        'ply'
    ],

    entry_points='''
        [console_scripts]
        soda=soda.app:main
    ''',
)