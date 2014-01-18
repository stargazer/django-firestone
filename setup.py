try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="django-gatorade",
    packages=('gatorade', ),
    version="0.1",
    description="REST API Framework",
    author="C. Paschalides",
    author_email="already.late@gmail.com",
    license="WTFPL",
    url="http://github.com/stargazer/django-gatorade",
    keywords=("rest", "restful", "api", "crud"),
    install_requires=(
        "Django==1.5.4",
    ),
    zip_safe=False,
    classifiers=(
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: Freely Distributable",
        "Development Status :: 1 - Planning",
    ),
)                                                    

