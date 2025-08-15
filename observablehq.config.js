// See https://observablehq.com/framework/config for documentation.

// Create DB to evaluate page loaders
import { DuckDBInstance } from '@duckdb/node-api';const duckdb_instance = await DuckDBInstance.create()
const db = await duckdb_instance.connect()
await db.run(`CREATE TABLE shows AS 
SELECT * 
FROM read_json('./py/out/*.json', 
  columns = {
    id: 'VARCHAR[]', 
    name: 'VARCHAR', 
    promotion: 'STRUCT(id BIGINT, "name" VARCHAR)', 
    arena: 'VARCHAR', 
    date: 'DATE', 
    matches: 'STRUCT(
        "type" VARCHAR, 
        result VARCHAR, 
        won DOUBLE, 
        cagematch DOUBLE, 
        wrestlers STRUCT(id BIGINT, "text" VARCHAR)[], 
        teams STRUCT(id BIGINT, "text" VARCHAR)[], 
        appearances STRUCT(id BIGINT, "text" VARCHAR)[])[]', 
    partial: 'BOOLEAN', 
    exclude: 'BOOLEAN'
  }
);`)

export default {
  // The app’s title; used in the sidebar and webpage titles.
  title: "TABLEMATCH",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  // pages: [
  //   {
  //     name: "Examples",
  //     pages: [
  //       {name: "Dashboard", path: "/example-dashboard"},
  //       {name: "Report", path: "/example-report"}
  //     ]
  //   }
  // ],

  // Content to add to the head of the page, e.g. for a favicon:
  head: '<link rel="icon" href="observable.png" type="image/png" sizes="32x32">',

  // The path to the source root.
  root: "src",

  // Some additional configuration options and their defaults:
  // theme: "default", // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  // footer: "Built with Observable.", // what to show in the footer (HTML)
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs

  async *dynamicPaths() {
    const show_ids = await db.runAndReadAll(`SELECT DISTINCT id AS show_id FROM shows`);
    for await (const {show_id} of show_ids.getRowObjects()) {
      yield `/shows/[${show_id.items}]`;
    }

    const wrestler_ids = await db.runAndReadAll(`
                FROM (
                  FROM (
                    FROM (
                      FROM shows
                      SELECT matches
                    )
                    SELECT unnest(matches, recursive := true)
                  )
                  SELECT unnest(wrestlers, recursive := true)
                )
                SELECT id AS wrestler_id
                GROUP BY id;`);

    for await (const {wrestler_id} of wrestler_ids.getRowObjects()) {
      yield `/wrestlers/${wrestler_id}`;
    }
  }
};
