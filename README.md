# The world is better than you think

A two-minute guess-then-reveal quiz on five sourced measures of human progress.
Each answer shows the data, the source, and what is still unsolved.

**Take it: https://better-than-you-think.vercel.app**

- `site/index.html`: standalone page, no build step, no tracking. Deploy to any static host.
- `progress-quiz.html`: the first version, kept as the artifact source.
- `site/partners.html`: embed code for partner sites, with live results.
- `api/r.js`, `api/stats.js`: anonymous measurement (Vercel Blob).

## Measurement

Each visitor is randomly asked "All things considered, do you think the world is getting better or worse?" either before the quiz (control) or after it (treatment). Only completed quizzes are stored: arm, answer, score, `?ref=` tag, language. No cookies, no IP, no personal data. The difference in the "getting better" share between arms estimates the quiz's effect. Live: https://better-than-you-think.vercel.app/api/stats

## Sources

| Measure | Then | Now | Source |
|---|---|---|---|
| Share living on < $3/day | 36% (2000) | 10% (2024) | World Bank PIP via Our World in Data |
| Under-5 mortality per 1,000 | 93 (1990) | 37 (2023) | UN IGME 2024 |
| Life expectancy | 46.5 (1950) | 73 (2023) | UN WPP 2024 via Our World in Data |
| Adult literacy | 12% (1820) | 87% (today) | Our World in Data |
| Utility solar LCOE (USD/kWh) | 0.417 (2010) | 0.043 (2024) | IRENA 2024 |

License: MIT.
