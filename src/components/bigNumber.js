import {html} from "npm:htl";

export function bigNumber(title, value, sub, width) {
  return html`
  <div style="font-size: ${width / 320}rem;
              font-style: initial;
              font-weight: 500;">${title}</div>
  <div style="font-size: ${width / 70}rem;
              font-weight: 900;
              display: inline-block;
              background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
              margin-bottom: -0.18em">${value}</div>
  <div class="muted" style="font-size: ${width / 430}rem;">${sub}</div>`;
}