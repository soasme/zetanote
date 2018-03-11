import setuptools

setuptools.setup(
    name='zetanote',
    version='0.0.1',
    url='https://github.com/soasme/zetanote',
    license='GPLv3',
    description='Zete note service.',
    author='Ju Lin <soasme@gmail.com>',
    packages=setuptools.find_packages(exclude=('tests', 'tests.*', '*.tests', '*.tests.*', )),
    package_dir={'zetanote': 'zetanote'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click',
        'tinydb',
        'flask',
        'bleach',
        'markdown',
        'authlib',
    ],
    entry_points='''
        [console_scripts]
        zeta=zetanote.cli:zetanote
    ''',
    test_require=['pytest', 'flake8'],
    platforms='linux',
    keywords=['note', 'text', 'service', 'web'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        ]
)
