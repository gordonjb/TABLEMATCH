// https://observablehq.com/@d3/donut-chart/2

import * as d3 from "npm:d3";

export function DonutChart(data, {centerText, width, height}) {
  //const height = width/2;
  const radius = Math.min(width, height) / 2;
  const arc = d3
    .arc()
    .innerRadius(radius * 0.6)
    .outerRadius(radius - 1);

  const pie = d3
    .pie()
    .padAngle(2 / radius)
    .sort(null)
    .value((d) => d.count);

  const color = d3.scaleOrdinal()
          .domain(data.map(d => Array.from(d.names).join(" / ")))
          .range(d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length).reverse())

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-width / 2, -height / 2, width, height])
    .attr("style", "max-width: 100%; height: auto;");

  svg
    .append("g")
    .selectAll()
    .data(pie(data))
    .join("path")
    .attr("fill", (d) => color(d.data.names))
    .attr("d", arc);

  svg
    .append("g")
    .attr("font-family", "sans-serif")
    .attr("font-size", 10)
    .attr("text-anchor", "middle")
    .selectAll()
    .data(pie(data))
    .join("text")
    .attr("transform", (d) => `translate(${arc.centroid(d)})`)
    .call((text) =>
      text
        .append("tspan")
        .filter((d) => d.endAngle - d.startAngle > 0.1)
        .attr("y", "-0.3em")
        .attr("font-weight", "bold")
        .attr("fill", "white")
        .text((d) => Array.from(d.data.names).join(" / "))
    )
    .call((text) =>
      text
        .filter((d) => d.endAngle - d.startAngle > 0.1)
        .append("tspan")
        .attr("x", 0)
        .attr("y", "0.8em")
        .attr("fill", "white")
        .attr("fill-opacity", 1)
        .text((d) => d.data.count)
    );

  svg
    .append("text")
    .attr("text-anchor", "middle")
    .attr("font-family", "sans-serif")
    .attr("font-size", "0.9rem")
    .attr("fill", "currentColor")
    .attr("font-weight", 600)
    .text(centerText);

  return svg.node();
}
