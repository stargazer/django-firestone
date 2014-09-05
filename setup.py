from setuptools import setup
from firestone import __version__

setup(
    name='django-firestone',
    packages=('firestone', ),
    version=__version__,
    description='REST API Framework',
    author='C. Paschalides',
    author_email='already.late@gmail.com',
    license='WTFPL',
    url='http://github.com/stargazer/django-firestone',
    keywords=('firestone', 'django-firestone', 'rest', 'restful', 'api', 'crud'),
    install_requires=(
        'Django',
        'django-preserialize',
        'django-endless-pagination',
        'pyJWT',
        'django-extensions', # Required to interact easily with the testproject
        'model-mommy',       # Required for the tests
        'coverage',          # Required for test coverage on Travis C.I.
        'sphinx_rtd_theme',  # Sphinx theme
        'tablib',            # For excel serialization
    ),
    tests_require=(),       # Kept it empty and instead moved all dependencies on
                            # ``install_requires``, which makes for way better dependency
                            # resolution.    
    test_suite='runtests.run',
    zip_safe=False,
    classifiers=(
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Development Status :: 4 - Beta',
    ),
)                                                    

