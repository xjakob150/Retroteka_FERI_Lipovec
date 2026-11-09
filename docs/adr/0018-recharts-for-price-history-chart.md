# Draw the price history chart with Recharts

## Context and Problem Statement

The item page shows how an item's estimated price changed over time (US-15): a line chart of the price checks with dates on one axis and prices on the other, shown from two checks on. Checks without listings have no price. The chart must work at phone width, and the frontend so far uses only React, React Router, Axios and Tailwind ([ADR-0001](0001-separate-react-spa-and-rest-api.md)).

How should the frontend draw the chart?

## Decision Drivers

* The chart is needed now for one line, and later charts are likely (collection statistics, US-20).
* It must fit the width of a phone without horizontal scrolling.
* Hover details, such as the date and price of a point, are useful on a chart with many checks.
* Few dependencies, since every package has to be installed in the frontend container and kept up to date.

## Considered Options

* Recharts
* Hand-written SVG in a React component
* Chart.js with `react-chartjs-2`

## Decision Outcome

Chosen option: "Recharts", because it is built from React components, so the chart is written as JSX like the rest of the frontend, and it gives axes, tooltips, gaps for missing values and responsive sizing without custom code. It can also draw the bar and pie charts that collection statistics will need, so later charts do not need another library.

### Consequences

* Good, because axes, tooltips and resizing come from the library, and the chart component stays short.
* Good, because a check without a price is passed as `null` and shown as a gap in the line.
* Good, because the same library can be reused for collection statistics (US-20).
* Bad, because the frontend gets a sizeable dependency for one chart, which increases the bundle downloaded on every page.
* Bad, because the library's look has to be adjusted to match the Tailwind styling, through props instead of classes.
* Neutral, because `node_modules` lives in an anonymous volume, so after adding it the containers must be rebuilt with `docker compose up --build -V`.

### Confirmation

The frontend builds with Recharts listed in `package.json`, and the item page is checked in the browser: with at least two checks the chart is drawn, a check without a price leaves a gap, and at phone width there is no horizontal scrolling.

## Pros and Cons of the Options

### Recharts

* Good, because it is declarative React components and supports React 19.
* Good, because it covers line, bar and pie charts.
* Bad, because it is the largest of the options in the bundle.

### Hand-written SVG in a React component

* Good, because it adds no dependency and all of the code is visible in the project.
* Good, because `viewBox` makes it scale to any width.
* Bad, because axes, tick labels, spacing by date and tooltips have to be written and tested by hand, and again for every later chart.

### Chart.js with `react-chartjs-2`

* Good, because it is widely used and draws on a canvas, which is fast with many points.
* Bad, because it is configured with an options object instead of components, and needs a wrapper package to be used from React.
* Bad, because a canvas is harder to style with the rest of the page and to read with a screen reader.

## More Information

* US-15 and US-20 in [05 – User Stories](../05-uporabniske-zgodbe.md); wireframe 6 in [06 – Wireframes](../06-wireframes.md).
* Related: [ADR-0001](0001-separate-react-spa-and-rest-api.md), [ADR-0013](0013-price-history-with-latest-price-on-item.md).
