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

~~~sql id=[showData]
SET VARIABLE s_id = ${id};
SELECT * FROM shows.shows WHERE list_has_all(id, CAST (getvariable('s_id') AS VARCHAR[])) LIMIT 1;
~~~

~~~js
// HTML Doc
display(html\`
<h1>\${showData.name}</h1>
<h2 class="muted">\${d3.utcFormat("%B %d, %Y")(new Date(showData.date))} - \${showData.arena} - \${showData.promotion.name}</h2>
<h4>Card Link:\${RenderLinks(Array.from(showData.id))}</h4>
<div class="grid grid-cols-1" style="grid-auto-rows: auto;">
  \${RenderMatches(Array.from(showData.matches))}
</div>
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
  return html.fragment\`\${ids.map((i) => html.fragment\` <a href="https://www.cagematch.net/?id=1&nr=\${i}">\${cmlink.cloneNode()}</a>\`)}\`
}

function RenderMatches(matches) {
  return html.fragment\`\${matches.map((m) => html.fragment\`
  <div class="card">
    <h3>\${m.type}</h3>
    <div class="mresult">\${m.result}</div>
    <div class="muted">\${m.won != null || m.cagematch != null ? RenderRatings(m.won, m.cagematch) : ""}</div>
  </div>
  \`)}\`
}

function RenderRatings(won, cm) {
  return html.fragment\`
  \${won != null ? html.fragment\`\${wonlogo.cloneNode()}: \${won}\` : ""}
  \${cm != null ? html.fragment\`\${cmlink.cloneNode()}: \${cm}\` : ""}
  \`
}
~~~
`);