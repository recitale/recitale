Installation
============

Requirements
-------------

Ubuntu/Debian
~~~~~~~~~~~~~

We need Python, pip and virtualenv::

    apt-get install python3-pip python3-virtualenv

If you plan on sharing video or audio files, we also need ffmpeg::

    apt-get install ffmpeg

If you plan on using recitale for uploading the generated website, we additionally need rsync::
  
    apt-get install rsync

Mac
~~~

We need Brew::

  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

If you plan on sharing video or audio files, we also need ffmpeg::
  
  brew install ffmpeg

If you plan on using recitale for uploading the generated website, we additionally need rsync::

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

See https://github.com/recitale/recitale/pkgs/container/recitale for fetching instructions and the list of all available images.
