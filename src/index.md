---
theme: dashboard
---

```js
// Imports
import {DonutChart} from "./components/donutChart.js";
import {bigNumber} from "./components/bigNumber.js";

//Load files async
const allWrestlers = FileAttachment("data/index/wrestlertable.parquet").parquet();
const allPromotions = FileAttachment("data/index/promotionstable.parquet").parquet();
const allMatches = FileAttachment("data/index/matchtable.parquet").parquet();
const stats = FileAttachment("data/index/statstable.parquet").parquet();
```

```js
//Destructure stats
const [{included: includedShows, excluded: excludedShows}] = stats
```

<h1>TABLEMATCH</h1>
<h2>THE PERSONAL WRESTLING DATABASE</h2>

<div class="grid grid-cols-4 hero">
  <div class="card">
    ${resize((width) => bigNumber("Wrestlers seen", allWrestlers.numRows, "", width))}
    
  </div>
  <div class="card">
    ${resize((width) => bigNumber("Matches seen", allMatches.numRows, "", width))}

  </div>
  <div class="card">
    ${resize((width) => bigNumber("Shows seen", includedShows, "+" + excludedShows + " partial shows excluded from count", width))}

  </div>
  <div class="card">
    ${resize((width) => bigNumber("Promotions seen", allPromotions.numRows, "", width))}

  </div>
</div>

<div class="grid grid-cols-2">
  <div class="card" style="padding: 0;">
    <div style="padding: 1em">
      ${display(tableSearch)}
    </div>
    ${display(Inputs.table(tableSearchValue,
      {
        columns: [
          "names",
          "count"
        ],
        header:
          {
            names: "Wrestler name(s)",
            count: "Match count",
          },
        sort: "count", reverse: true,
        select: false,
        format: {names: (value, i, data) => htl.html`<a href="./wrestlers/${data[i].id}">${Array.from(value).join(" / ")}</a>`},
        rows: 21,
        height: 505
      }
    ))}
  </div>

  <div class="card">
    ${resize((width, height) => DonutChart([...allPromotions], {centerText: "Promotions", width, height}))}
  </div>
</div>

```js
// Create search input (for searchable table)
const tableSearch = Inputs.search(allWrestlers, {format: (x) => ""});

const tableSearchValue = view(tableSearch);
```

<style>

.hero {
  font-family: var(--sans-serif);
  text-wrap: balance;
}

</style>
