import setuptools

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='wagtail-extensions',
    use_scm_version={'version_scheme': 'post-release'},
    author='Interaction Consortium',
    author_email='studio@interaction.net.au',
    url='https://github.com/ixc/wagtail-extensions',
    description='Extensions to help us build Wagtail sites',
    long_description=long_description,
    license='MIT',
    packages=setuptools.find_packages(),
    scripts=[],
    include_package_data=True,
    install_requires=[
        'Django',
        'Wagtail',
        'Cerberus',  # Validation of dict/JSON data
        'django-prettyjson',  # Pretty widget UI for `JSONField`s
    ],
    extras_require={},
    setup_requires=['setuptools_scm'],
)
