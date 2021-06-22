import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='django-docrootcms',
      version='2.2',
      description='The missing app for developers creating and maintaining websites',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/sstacha/django-docrootcms',
      author='Steve Stacha',
      author_email='sstacha@gmail.com',
      license='MIT',
      packages=setuptools.find_packages(exclude=["docroot"]),
      include_package_data=True,
      zip_safe=False,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
      ],
      python_requires='>=3.6',
      install_requires=[
          'django',
      ],
)
