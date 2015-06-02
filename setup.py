from setuptools import setup, find_packages

setup(
    name='tuhi-gtk',
    version='0.1',
    license='GPL3',
    author='icasdri',
    author_email='icasdri@gmail.com',
    description='Simple self-hosted synchronized notes (GTK client)',
    url='https://github.com/icasdri/tuhi-gtk',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    data_files=[('/usr/share/applications', ['distributing/tuhi.desktop'])],
    packages=find_packages(),
    entry_points={
        'gui_scripts': ['tuhi = tuhi_gtk.main:main'],
    }
)
