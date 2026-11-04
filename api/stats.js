import { list } from "@vercel/blob";

// Aggregate completions. Control arm answers the outlook question before the quiz,
// treatment arm after it; the difference in "Getting better" share is the effect.
export default async function handler(req, res) {
  const recs = [];
  let cursor;
  do {
    const page = await list({ prefix: "r/", cursor, limit: 1000 });
    const got = await Promise.all(page.blobs.map((x) => fetch(x.url).then((r) => r.json()).catch(() => null)));
    recs.push(...got.filter(Boolean));
    cursor = page.hasMore ? page.cursor : undefined;
  } while (cursor);

  const arm = (a) => {
    const s = recs.filter((r) => r.arm === a);
    const c = (o) => s.filter((r) => r.outlook === o).length;
    const n = s.length;
    return {
      n, better: c("Getting better"), neither: c("Neither better nor worse"), worse: c("Getting worse"),
      better_share: n ? +(c("Getting better") / n).toFixed(3) : null,
      mean_score: n ? +(s.reduce((t, r) => t + r.score, 0) / n).toFixed(2) : null,
    };
  };
  const control = arm("pre"), treatment = arm("post");
  const by_ref = {};
  for (const r of recs) by_ref[r.ref] = (by_ref[r.ref] || 0) + 1;
  res.setHeader("cache-control", "s-maxage=120, stale-while-revalidate=600");
  return res.json({
    completions: recs.length,
    control_asked_before_quiz: control,
    treatment_asked_after_quiz: treatment,
    effect_pp: control.better_share != null && treatment.better_share != null
      ? +((treatment.better_share - control.better_share) * 100).toFixed(1) : null,
    by_ref,
    note: "Randomized between-subjects. Only completed quizzes count. Small samples are noisy.",
  });
}
