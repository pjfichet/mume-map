# Mume mini mapper

This is a mini mapper for playing [MUME](https://mume.org "MUME Official Site").

It is simple and hackable fork of [mapperproxy-mume](https://github.com/nstockton/mapperproxy-mume), made for test purposes:
- while other mume mappers act as a telnet proxy, this one does not,
- it records room ids sent by mume's server, and uses them to sync the map.

---

![screenshot](https://github.com/pjfichet/mume-minimap/raw/master/tiles/tiles/screenshot-multi.png?raw=true "screenshot")

---

## License And Credits

The mapper is licensed under the Mozilla Public License, version 2.0.

The tiles of the GUI are distributed under the [CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/legalcode "CC-BY-SA 3.0 official site") license.
They are a modified version of [fantasy-tileset.png](https://opengameart.org/content/32x32-fantasy-tileset "fantasy-tileset page on OpenGameArt") originally created by [Jerome.](http://jerom-bd.blogspot.fr/ "Jerome old site")

## Installation

```
python -m venv venv
venv/bin/python -m pip install --editable .
```

## Usage

See [mume-tintin](https://github.com/pjfichet/mume-tintin) `tin/map.tin` file for an usage example with tintin++.

