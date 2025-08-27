import {parseArgs} from "node:util";

const {
  values: {id}
} = parseArgs({
  options: {id: {type: "string"}}
});

process.stdout.write(`---
theme: dashboard
---

~~~js
//Load files async
const shows = FileAttachment("../data/show-${id}/showtable.parquet").parquet();

// Images
const cmlink = FileAttachment("../img/cmlink.webp").image(
  {
    style: "display:inline-block; height:1em; width:auto; transform:translate(0, 0.1em)",
    alt: "Cagematch Logo"
  }
);

const wonlogo = FileAttachment("../img/won.png").image(
  {
    style: "display:inline-block; height:1em; width:auto; transform:translate(0, 0.1em)",
    alt: "Wrestling Observer Logo"
  }
);
~~~

~~~js
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

//Destructure shows
const [{id: showid, name: name, date: date, arena: arena, promotion: promotion, matches: matches}] = shows;

// HTML Doc
display(html\`
<h1>\${name}</h1>
<h2 class="muted">\${d3.utcFormat("%B %d, %Y")(new Date(date))} - \${arena} - \${promotion.name}</h2>
<h4>Card Link:\${RenderLinks(Array.from(showid))}</h4>
<div class="grid grid-cols-1" style="grid-auto-rows: auto;">
  \${RenderMatches(Array.from(matches))}
</div>
\`)
~~~
`);