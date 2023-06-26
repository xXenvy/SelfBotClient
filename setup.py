from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.1.1'
DESCRIPTION = 'Library that will allow you to manage selfbots'
LONG_DESCRIPTION = 'The library logs into your account thanks to the entered tokens and can manage them. ' \
                   'such as sending messages, deleting roles, etc.'

# Setting up
setup(
    name="selfbotclient",
    version=VERSION,
    author="xXenvy",
    author_email="<xpimepk01@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['colorlog', 'aiohttp'],
    keywords=['python', 'requests', 'discord selfbot', 'selfbot', 'discord.py', 'aiohttp'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)