from setuptools import setup, find_packages

setup(
    name='django-intersections',
    version=__import__('intersections').__version__,
    description='Django tool to show groups members intersections for social networks.',
    long_description=open('README.rst').read(),
    author='Dmitry Krupin',
    author_email='krupin.dv19@gmail.com',
    url='https://github.com/Andertaker/django-intersections',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-oauth-tokens>=0.2.2',
        'tweepy',
        'django-vkontakte-api>=0.8.2',
        'django-facebook==6.0.3',
        'Pillow', # needed for django-facebook
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
