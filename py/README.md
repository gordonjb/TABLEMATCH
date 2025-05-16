# TABLEMATCH Python Parsing

## Description

These Python scripts take a YAML file of show links from [CAGEMATCH.net](https://www.cagematch.net), scrape each one, parse the info to a standard set of objects (see [`models/`](models/)) and outputs each one as a JSON file in the specified directory.

## Getting Started

### Dependencies

- [uv](https://docs.astral.sh/uv/)

### Technologies

- [Beautiful Soup](https://pypi.org/project/beautifulsoup4/)
- [Requests](https://requests.readthedocs.io/en/latest/)
- [requests-cache](https://requests-cache.readthedocs.io/en/stable/)
- [pyyaml](https://github.com/yaml/pyyaml)
- [Click](https://click.palletsprojects.com/en/stable/)

### Running

```sh
uv run main.py shows.yaml out
```

### Usage

```sh
$ uv run main.py --help

Usage: main.py [OPTIONS] FILENAME DESTINATION

  Parse path FILENAME, outputting YAML representations of the shows in folder
  DESTINATION, which will be created if it does not exist. Existing files will
  be overwritten if they clash.

Options:
  --loglevel [CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|NOTSET]
                                  Set the Python logging level.  [default:
                                  WARNING]
  --help                          Show this message and exit.
```

## YAML Spec

The list of attended shows is sourced from a [YAML](https://yaml.org/) file. My personal copy is at [`shows.yaml`](shows.yaml).

### The List

At it's most basic, the file is just a top level YAML list of show URLs:

```yaml
- https://www.cagematch.net/?id=1&nr=244194
- https://www.cagematch.net/?id=1&nr=241265
- https://www.cagematch.net/?id=1&nr=244175
```

To add shows to the list that will be considered, add a new line containing the text `- ` followed by the URL of the show page from CAGEMATCH. The `- ` syntax creates a list in YAML.

### Comments

You can also use comments to help you identify links in any way you choose. Comments are created by typing `#`. All text that follows on that line will be ignored when the file is loaded in. This makes it easy to keep track of which URL is which. For instance you could indicate the show with a comment at the end of the line:

```yaml
- https://www.cagematch.net/?id=1&nr=425337 # NOAH Sunny Voyage 2025
- https://www.cagematch.net/?id=1&nr=417742 # AEW Dynasty 2025
#- https://www.cagematch.net/?id=1&nr=419740 This link will be ignored, for example
```

or you could use comment lines:

```yaml
# NOAH Sunny Voyage 2025
- https://www.cagematch.net/?id=1&nr=242190
# AEW Dynasty 2025
- https://www.cagematch.net/?id=1&nr=417742
# This link will be ignored, for example:
#- https://www.cagematch.net/?id=1&nr=419740
```

or however you choose. In my personal file, I've used whole line comments to separate months and then added show names at the end of each line.

### Keywords

Not every entry is just a URL however. Special types of shows can be created using certain keywords. The following keywords are supported:

**_Note_: indentation is important in YAML. You should follow the indentation patterns in the example below (i.e. each new level should be indented by 4 spaces).**

#### Combine Shows (`taping`)

When it comes to TV shows, CAGEMATCH tends to create a show page for each show even if they were taped in one go. If you want to stick these back together, the `taping` keyword will do this. To use it, use `taping:` as your top level list item, and then include an indented list of the show pages you want to be combined:

```yaml
- taping:
    - https://www.cagematch.net/?id=1&nr=94859 # WWE Friday Night SmackDown #714
    - https://www.cagematch.net/?id=1&nr=94858 # WWE Main Event #30
```

You can combine as many shows as you want together:

```yaml
- taping:
    - https://www.cagematch.net/?id=1&nr=129265
    - https://www.cagematch.net/?id=1&nr=129881
    - https://www.cagematch.net/?id=1&nr=130380
    - https://www.cagematch.net/?id=1&nr=127390
```

By default, the combined show will take the name of the first show listed, and add "Taping" to the end, for example "WWE Friday Night SmackDown #714 Taping" in the first example. The details of the first show listed will also be used (such as the promotion and date). The ID number of the show will be a list of all the shows that were combined.

If you want to specify a custom name, you can do this using the following syntax:

```yaml
- taping:
    name: "AEW All In London 2024"
    urls:
        - https://www.cagematch.net/?id=1&nr=401410 # AEW All In London 2024 - Zero Hour
        - https://www.cagematch.net/?id=1&nr=374482 # AEW All In London 2024
```

The `urls` key should contain the same show URL list as you would have entered (now indented another level), and the `name` key will be used for the combined show instead of the default.

#### Partial Shows (`partial`)

Sometimes, you didn't see an entire show. In this case, you can stop wrestlers you didn't see getting an appearance credit by indicating the matches that you missed using the `partial` keyword. For instance, to exclude the last two matches of [this show](https://www.cagematch.net/?id=1&nr=239089), do the following:

```yaml
- partial:
    url: https://www.cagematch.net/?id=1&nr=239089
    exclude: [4,5]
```

The `url` key indicates the show URL as you would have entered, and the `exclude` key indicates the matches you missed. This is a comma separated list, with the first match being match 1, regardless of if it's a dark match. The numbers don't need to be in order or continuous.

If you missed almost all of the show, you may not want to count it in your overall totals. In this case, use the `exclude_from_count` key:

```yaml
- partial:
    url: https://www.cagematch.net/?id=1&nr=236880
    exclude: [2,3,5]
    exclude_from_count: True
```

#### Combine Matches (`squashmatch`)

CAGEMATCH will sometimes list things you might consider as a single match as multiple separate matches. An example I found was a gauntlet match. For example, including [this show](https://www.cagematch.net/?id=1&nr=186905) normally would add 50 matches to Manami Toyota's count. If you would rather have this treated as one match, you can do the following:

```yaml
- squashmatch:
    url: https://www.cagematch.net/?id=1&nr=186905 # Manami Toyota ~ Retirement To The Universe
    squash: [2-51]
```

The `url` key indicates the show URL as you would have entered, and the `squash` key indicates the match range that should be combined. This is a comma separated list, formatted `start-end`. Multiple ranges can be provided in a list. No checking is done that these ranges are valid or make sense.

### Combining keywords

Keywords can be used anywhere a show URL would otherwise go, meaning you can combine the various keywords together. For example, you could combine part of one show with a complete other show:

```yaml
- taping:
    - partial:
        url: https://www.cagematch.net/?id=1&nr=242611
        exclude: [1]
    - https://www.cagematch.net/?id=1&nr=242612
```

```yaml
- taping:
    name: "WWE Friday Night SmackDown #556 Taping"
    urls:
        - https://www.cagematch.net/?id=1&nr=50217 # WWE NXT #1.08
        - partial:
            url: https://www.cagematch.net/?id=1&nr=50185 # WWE Superstars #53
            exclude: [2,3] # only one match
        - https://www.cagematch.net/?id=1&nr=50226 # WWE Friday Night SmackDown #556
```

The system is flexible enough that you could deeply nest keywords if you wanted:

```yaml
- taping:
    name: "WrestleMania Weekend"
    urls:
        - squashmatch:
            url: 
                taping:
                    name: "WWE World at WrestleMania 41"
                    urls:
                        - https://www.cagematch.net/?id=1&nr=424399
                        - https://www.cagematch.net/?id=1&nr=424400
                        - https://www.cagematch.net/?id=1&nr=424385
                        - partial:
                            url: https://www.cagematch.net/?id=1&nr=424401
                            exclude: [2]
            squash: [1-15]
        - https://www.cagematch.net/?id=1&nr=394375
        - taping:
            - https://www.cagematch.net/?id=1&nr=418372
            - https://www.cagematch.net/?id=1&nr=423692
        - https://www.cagematch.net/?id=1&nr=394376
```

### More examples

My personal shows.yaml is in the repo for more examples of using these keywords: [shows.yaml](shows.yaml)

## Caching

To avoid making too many requests, CAGEMATCH pages are cached locally when retrieved. The tool will print out as it loads whether a page was downloaded fresh or retrieved from the cache. If the information on a page has changed since it was first retrieved, deleting the cache database (`cagematch_cache.sqlite`) will cause all pages to be reloaded on the next run.
