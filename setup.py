from setuptools import setup, find_packages
import os
import skwissh

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: French',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: System :: Monitoring',
]

setup(
    author="Roland Saikali",
    author_email="contact@skwissh.com",
    name='django-skwissh',
    version=skwissh.__version__,
    description='SSH monitoring application',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://skwissh.com/',
    download_url='https://github.com/rsaikali/django-skwissh',
    license='GNU General Public License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django==1.4.1',
        'Fabric==1.4.3',
        'nose',
        'django-extra-views==0.2.5',
        'django-kronos==0.3',
    ],
    packages=find_packages(exclude=['skwissh.migrations', ]),
    package_data={'': [
        'templates/*.html',
        'templates/*.js',
        'templates/base/*.html',
        'static/skwissh/images/foundation/orbit/*',
        'static/skwissh/images/skwissh/*',
        'static/skwissh/javascripts/*',
        'static/skwissh/stylesheets/*',
        'locale/*/LC_MESSAGES/*',
        'fixtures/*.json',
    ]},
    include_package_data=True,
)
