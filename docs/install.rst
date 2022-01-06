Installation
============

Requirements
-------------

Ubuntu/Debian
~~~~~~~~~~~~~

We need Python, pip and virtualenv::

    apt-get install python3-pip python3-virtualenv

And a video converter like ffmpeg::

    apt-get install ffmpeg

or::

    apt-get install libav-tools

For deployment, we need rsync::
  
    apt-get install rsync

Mac
~~~

We need Brew::

  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

And a video converter like ffmpeg::
  
  brew install ffmpeg

For deployment, we need rsync::

  brew install rsync

Installation in virtualenv
--------------------------

1. Create a virtualenv, and activate it::

    virtualenv ve
    source ve/bin/activate

2. Download and install recitale::

    pip3 install recitale
   
Container
---------

A container image is available at ghcr.io/recitale/recitale. One can build their website by running the following command::

   docker run --rm -v <PATH_TO_GALLERY_SOURCE>:/var/www ghcr.io/recitale/recitale build

See https://github.com/orgs/recitale/packages/container/package/recitale%2Frecitale for fetching instructions and the list of all available images.
