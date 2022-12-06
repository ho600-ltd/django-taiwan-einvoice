import datetime, re, os
from setuptools import setup, find_packages

DESCRIPTION = 'Django-Taiwan-EInvoice'
LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except:
    LONG_DESCRIPTION = ''

try:
    REQUIREMENTS = open('requirements.txt').read()
except:
    REQUIREMENTS = []

install_requires = [r for r in REQUIREMENTS.split('\n') if r
                    and not re.match('^ *#.*', r)
                    and not re.match('^.*git\+.*', r)
                    and not re.match('^.*ssh:.*', r)
                    and not re.match('^.*https?:.*', r)
                   ]

def package_static_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.endswith('py'):
                continue
            paths.append(os.path.join('..', path, filename))
    return paths


setup(name='taiwan_einvoice',
      install_requires=install_requires,
      version='0.3.4',
      packages=[
                'taiwan_einvoice',
                'taiwan_einvoice.migrations',
                'taiwan_einvoice_docs',
                ],
      package_dir={
                   'taiwan_einvoice': 'taiwan_einvoice',
                   'taiwan_einvoice.migrations': 'taiwan_einvoice/migrations',
                   'taiwan_einvoice_docs': 'docs',
                  },
      package_data={
                    'taiwan_einvoice': [
                        'static/taiwan_einvoice/assets/*.css',
                        'static/taiwan_einvoice/assets/*.js',
                        'static/taiwan_einvoice/assets/*.svg',
                        'static/taiwan_einvoice/*.css',
                        'static/taiwan_einvoice/*.js',
                        'templates/taiwan_einvoice/*.html',
                        'locale/zh_Hant/LC_MESSAGES/*.po',
                       ],
                    'taiwan_einvoice_docs': package_static_files('./docs'),
      },
      author='hoamon',
      author_email='hoamon@ho600.com',
      url='https://github.com/ho600-ltd/django-taiwan-einvoice/',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
      classifiers=[
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Operating System :: Linux/Raspberry Pi OS',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: MIT License',
      ],
)
