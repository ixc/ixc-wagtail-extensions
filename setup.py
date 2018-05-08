import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='ixc-wagtail-extensions',
    use_scm_version={'version_scheme': 'post-release'},
    author='Interaction Consortium',
    author_email='studio@interaction.net.au',
    url='https://github.com/ixc/ixc-wagtail-extensions',
    description='Extensions to help us build Wagtail sites',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=setuptools.find_packages(),
    scripts=[],
    include_package_data=True,
    install_requires=[
        'Django',
        'Wagtail',
        'django-prettyjson',  # Pretty widget UI for `JSONField`s
    ],
    extras_require={},
    setup_requires=['setuptools_scm'],
)
