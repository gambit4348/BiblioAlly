from distutils.core import setup


setup(
  name='BiblioAlly',
  packages=['BiblioAlly'],
  version='0.0.4',
  license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description='A helper for scientific literature reviews',
  author='Alex Sebastião Constâncio',
  author_email='gambit4348@gmail.com',
  url='https://github.com/gambit4348/BiblioAlly',
  download_url='https://github.com/gambit4348/BiblioAlly/archive/refs/tags/v0.0.4.tar.gz',
  keywords=['Science', 'Literature review', 'Articles'],
  install_requires=[
    'arpeggio',
    'matplotlib',
    'PySimpleGUI',
    'sqlalchemy',
  ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
  ],
)

