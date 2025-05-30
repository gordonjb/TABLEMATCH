# TABLEMATCH

TABLEMATCH scrapes a list of shows from [CAGEMATCH.net](https://www.cagematch.net) and generates a static site of statistics about those shows.

## Description

TABLEMATCH uses [Observable Framework](https://observablehq.com/framework/) to visualise statistics about wrestling shows in the style of something like [setlist.fm](https://www.setlist.fm/concerts/gordonjb). It gets its data from a [list of shows](py/shows.yaml) scraped from CAGEMATCH.net and parsed to a standard JSON format by a Python CLI library (see its [`README`](/py/README.md) for more info). These are then loaded into a [DuckDB](https://duckdb.org/) database by a dataloader, which is then used to calculate stats.

## Getting Started

### Dependencies

- [Node.js](https://nodejs.org/en/download)
- [uv](https://docs.astral.sh/uv/)
- [DuckDB](https://duckdb.org/)

### Building

First to convert the list of shows to JSON:

```sh
cd py/
uv run main.py shows.yaml out
```

To run a local autoupdating server:

```sh
npm run dev
```

To build a static site as a `/dist` folder:

```sh
npm run build
```

### Technologies

- [Observable Framework](https://observablehq.com/framework/), see also the Framework README at [`README-Framework.md`](README-Framework.md)
- See [Python dependencies in the README in the Python folder](py/README.md#technologies)

## Shows list

The list of attended shows is sourced from a [YAML](https://yaml.org/) file. My personal copy for reference is at [`py/shows.yaml`](py/shows.yaml).

At it's most basic, the file is just a top level YAML list of show URLs:

```yaml
- https://www.cagematch.net/?id=1&nr=244194
- https://www.cagematch.net/?id=1&nr=241265
- https://www.cagematch.net/?id=1&nr=244175
```

For more in depth info on the options and Python script, check the [README in the Python folder](py/README.md#yaml-spec).

## Custom shows

The site expects to load JSON files representing shows from [`py/out/`](py/out/). While these can be generated by the Python CLI, you can also write your own, for example for shows that CAGEMATCH doesn't have in it's database. Use the example of a show generated by the CLI as comparison, and keep it in `py/out/`. The CLI will only overwrite your file if it has the same name as one it generates.
