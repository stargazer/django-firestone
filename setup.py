from setuptools import setup

setup(
    name='django-firestone',
    packages=('firestone', ),
    version='0.2',
    description='REST API Framework',
    author='C. Paschalides',
    author_email='already.late@gmail.com',
    license='WTFPL',
    url='http://github.com/stargazer/django-firestone',
    keywords=('firestone', 'django-firestone', 'rest', 'restful', 'api', 'crud'),
    install_requires=(
        'Django>=1.5.4',
        'django-preserialize',
        'django-extensions', # Required to interact easily with the testproject
        'model-mommy',       # Required for the tests
        'coverage',          # Required for test coverage on Travis C.I.
    ),
    tests_require=(),       # Kept it empty and instead moved all dependencies on
                            # ``install_requires``, which makes for way better dependency
                            # resolution.    
    test_suite='runtests.runtests',
    zip_safe=False,
    classifiers=(
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Development Status :: 3 - Alpha',
    ),
)                                                    

