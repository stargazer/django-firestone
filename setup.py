from setuptools import setup

setup(
    name='django-firestone',
    packages=('firestone', ),
    version='0.1',
    description='REST API Framework',
    author='C. Paschalides',
    author_email='already.late@gmail.com',
    license='WTFPL',
    url='http://github.com/stargazer/django-firestone',
    keywords=('firestone', 'django-firestone', 'rest', 'restful', 'api', 'crud'),
    install_requires=(
        'Django==1.5.4',
        'django-preserialize==1.0.5',
    ),
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

