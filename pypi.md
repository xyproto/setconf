# Uploading to Pypi

## The old deprecated way

    sudo pacman -S python-pip python-setuptools python-wheel python-twine --needed
    python setup.py sdist bdist_wheel

Have a good `~/.pypirc` file, before uploading to the server, then be prepared to pgp sign and:

    twine upload --sign dist/setconf-0.7.6*

# Upload to pypi

    python setup.py sdist upload -r pypi

