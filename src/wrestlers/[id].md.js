import {parseArgs} from "node:util";

const {
  values: {id}
} = parseArgs({
  options: {id: {type: "string"}}
});

process.stdout.write(`---
theme: dashboard
sql:
  shows: ../data/shows.db
---

~~~sql id=[...showData]
SET VARIABLE w_id = ${id};
SELECT * REPLACE (list_filter(matches, m -> len(list_filter(m.wrestlers, w -> w.id = getvariable('w_id'))) > 0) as matches) FROM shows.shows WHERE len(list_filter(matches, m -> len(list_filter(m.wrestlers, w -> w.id = getvariable('w_id'))) > 0)) > 0 ORDER BY date;
~~~

~~~sql id="[{count: metaCount, names: metaNames, pcount: metaPromCount}]"
    SET VARIABLE w_id = ${id};
    FROM (
      FROM (
        FROM (
          FROM shows.shows
          SELECT matches, promotion
          ORDER BY date
        )
        SELECT unnest(matches, recursive := true), promotion.id AS promotionid
      )
      SELECT unnest(wrestlers, recursive := true), promotionid
    )
    SELECT id, count(id) AS count, count(DISTINCT promotionid) AS pcount, shows.list_order_by_count(array_agg(text)) as names
    WHERE id = getvariable ('w_id')
    GROUP BY id ORDER BY count DESC;
~~~

~~~js
// HTML Doc
display(html\`
<h1>\${Array.from(metaNames).join(" / ")}</h1>
<h2 class="muted">\${metaCount} matches - \${showData.length} shows - \${metaPromCount} promotions</h2>
<h4>Profile Link:\${RenderLinks(Array.of(${id}))}</h4>
<div class="muted">First seen \${d3.utcFormat("%B %d, %Y")(new Date(showData.at(0).date))} - Last seen \${d3.utcFormat("%B %d, %Y")(new Date(showData.at(-1).date))}</div>
<hr>
\${RenderShows(showData)}
\`)
~~~

~~~js
// Images
const cmlink = await FileAttachment("../img/cmlink.webp").image(
  {
    style: "display:inline-block; height:1em; width:auto; transform:translate(0, 0.1em)",
    alt: "Cagematch Logo"
  }
);

const wonlogo = await FileAttachment("../img/won.png").image(
  {
    style: "display:inline-block; height:1em; width:auto; transform:translate(0, 0.1em)",
    alt: "Wrestling Observer Logo"
  }
);

// Functions
function RenderLinks(ids) {
  return html.fragment\`\${ids.map((i) => html.fragment\` <a href="https://www.cagematch.net/?id=2&nr=\${i}">\${cmlink.cloneNode()}</a>\`)}\`
}

function RenderShows(shows) {
  return html.fragment\`\${shows.map((s) => html.fragment\`
  <div class="show">
    <div><a href="../shows/\${s.id}">\${s.name}</a></div> <div class="muted">\${d3.utcFormat("%B %d, %Y")(new Date(s.date))} - \${s.arena} - \${s.promotion.name}</div>
    <div class="grid grid-cols-1" style="grid-auto-rows: auto;">
      \${RenderMatches(Array.from(s.matches))}
    </div>
  </div>
  \`)}\`
}

function RenderMatches(matches) {
  return html.fragment\`\${matches.map((m) => html.fragment\`
  <div class="card"}">
    <h3>\${m.type}</h3>
    <div class="mresult">\${m.result}</div>
    <div class="muted">\${m.won != null || m.cagematch != null ? RenderRatings(m.won, m.cagematch) : ""}</div>
  </div>
  \`)}\`
}

function RenderRatings(won, cm) {
  return html.fragment\`
  \${won != null ? html.fragment\`\${wonlogo.cloneNode()} - \${won}\` : ""}
  \${cm != null ? html.fragment\`\${cmlink.cloneNode()} - \${cm}\` : ""}
  \`
}
~~~
`);