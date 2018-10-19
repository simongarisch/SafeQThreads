from setuptools import setup, find_packages

setup(name="safeqthreads",
      version="0.0.1",
      install_requires=[
          "QtPy>=1.5.0"
        ],
      description="Track and manage your QThreads.",
      long_description=open("README.md").read(),

      author="Simon Garisch",
      author_email="gatman946@gmail.com",
      url="https://github.com/simongarisch/safeqthreads",
      packages=find_packages()
     )
