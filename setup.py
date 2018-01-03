from setuptools import setup


setup(
  name = "pybots",
  packages = ["pybots", "pybots.base", "pybots.ctf"],
  version = "1.0.3",
  license = "AGPLv3",
  description = "A library for quickly creating client bots for communicating "
                "with remote hosts.",
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  url = "https://github.com/dhondta/pybots",
  keywords = ["Bot", "client", "socket", "netcat", "http", "json", "epassport", "irc", "ringzer0", "rootme"],
  classifiers = [
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
)
