---
theme: dashboard
sql:
  shows: data/shows.db
---

```js
import {DonutChart} from "./components/donutChart.js";
import {bigNumber} from "./components/bigNumber.js";
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
    ${resize((width) => bigNumber("Shows seen", includedShows.numRows, "+" + excludedShows.numRows + " partial shows excluded from count", width))}

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
        format: {names: (x) => Array.from(x).join(" / ")},
        rows: 21
      }
    ))}
  </div>

  <div class="card">
    ${resize((width, height) => DonutChart(allPromotions.toArray(), {centerText: "Promotions", width, height}))}
  </div>
</div>

```js
// Create search input (for searchable table)
const tableSearch = Inputs.search(allWrestlers, {format: (x) => ""});

const tableSearchValue = view(tableSearch);
```

```sql id=allWrestlers
    SELECT id, count(id) as count, list_distinct(array_agg(text)) as names from (SELECT unnest(wrestlers, recursive := true) from (SELECT unnest(matches, recursive := true) FROM shows.shows)) GROUP BY id ORDER BY count DESC;
```

```sql id=allShows
    SELECT * FROM shows.shows ORDER BY date;
```

```sql id=includedShows
    SELECT * FROM shows.shows WHERE exclude == false ORDER BY date;
```

```sql id=excludedShows
    SELECT * FROM shows.shows WHERE exclude == true ORDER BY date;
```

```sql id=allPromotions
    SELECT promotion.id as id, list_distinct(array_agg(promotion."name")) as names, count() as count FROM shows.shows GROUP BY ALL ORDER BY count DESC;
```

```sql id=allMatches
    SELECT unnest(matches, recursive := true) FROM (SELECT * FROM shows.shows ORDER BY date);
```

<style>

.hero {
  font-family: var(--sans-serif);
  text-wrap: balance;
}

</style>
