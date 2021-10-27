<p align="center">
<img src="logo.png">
</p>

# recitale

recitale. Static site generator for your story.

Make beautiful customizable pictures galleries that tell a story using a static website generator written in Python. You don't need to care about css, code and presentation, manage your contents in YAML file and recitale will take care about the rest.

recitale is sections oriented, make it very flexible, many kinds of section already available:

* Parallax
* Group of pics (gallery)
* Paragraph
* Iframe (Youtube, Maps, etc..)
* Quote
* [And more](http://prosopopee.readthedocs.io/en/latest/sections.html)

Important note: This project is considered in alpha state. There may be significant changes in configuration files, API or user interface at any time.

## Screenshots

<img src="https://github.com/recitale/recitale/raw/devel/pics/2018-04-30-113447_872x817_scrot.png" width="15%"></img> <img src="https://github.com/recitale/recitale/raw/devel/pics/2018-04-30-114059_1128x908_scrot.png" width="15%"></img> <img src="https://github.com/recitale/recitale/raw/devel/pics/2018-04-30-113707_1195x788_scrot.png" width="15%"></img> <img src="https://github.com/recitale/recitale/raw/devel/pics/2018-04-30-113821_1128x847_scrot.png" width="15%"></img> 

## Features

recitale currently supports:

 * Automatic generation
 * Lightweight
 * Thumbnails & multiple resolutions for fast previews (JPEG progressive)
 * Videos support
 * Mobile friendly
 * Caching for fast rendering
 * Multi level gallery
 * Support themes (default, material, light)
 * Password access (encrypt page)
 * Image lazy loading
 * Night Mode
 * Completely static output is easy to host anywhere
 * Hackable
 
  ## Examples
 
You can find example usages here:

* http://surleschemins.fr
* http://media.faimaison.net/photos/galerie/
* https://www.thebrownianmovement.org/
* http://outside.browny.pink
* http://www.street-art.me
 
 ## Code example

```yaml
title: Title
date: 2015-12-18
cover: P1070043-01-01.jpeg
sections:
  - type: full-picture
    image: P1060979-01-01.jpeg
    fixed: true
    text:
      title: My Story
      sub_title: some subtitle
      date: 2015-12-18
  - type: paragraph
    title: Beautiful Title
    text: Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor
  - type: pictures-group
    images:
      -
        - P1060938-01-01.jpeg
        - P1060946-01-01.jpeg
        - P1060947-01-01.jpeg
        - P1060948-01-01.jpeg
```
 
## Usage
```bash
  recitale
  recitale test
  recitale preview
  recitale deploy
  recitale autogen (-d <folder> | --all ) [--force]
  recitale (-h | --help)
  recitale --version
                                                                                
Options:                                                                        
  test          Verify all your yaml data                                       
  preview       Start preview webserver on port 8000                            
  deploy        Deploy your website                                             
  autogen       Generate gallery automaticaly                                   
  -h, --help    Show this screen.                                               
  --version     Show version.
```

## Docker

https://hub.docker.com/r/beudbeud/prosopopee/

## Licence 

GPL-3.0+

## Documentation

  http://prosopopee.readthedocs.org/en/latest/

## IRC 

channel : irc.freenode.net#prosopopee

## Origin

recitale started as a fork of [prosopopee](https://github.com/Psycojoker/prosopopee).

recitale is a contraction of `tale` and the French word `récit` which are both depicting the same thing: a story.

It is also a play on `recital` which is related to poetry reading.

recitale should be pronounced `/ʁe.siˈteɪl/` that is, the French pronounciation for [`récit`](https://en.wiktionary.org/wiki/r%C3%A9cit#Pronunciation) followed
by the English pronounciation of [`tale`](https://en.wiktionary.org/wiki/tale#Pronunciation).
