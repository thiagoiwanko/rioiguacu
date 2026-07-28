export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    const corsHeaders = {
      "Access-Control-Allow-Origin": "https://rioiguacu.com",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    if (url.pathname !== "/track") {
      return new Response("Not found", { status: 404, headers: corsHeaders });
    }

    const dateStr = new Intl.DateTimeFormat("en-CA", {
      timeZone: "America/Sao_Paulo",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date());

    const weekKey = isoWeekKey(dateStr);

    const id = env.COUNTER.idFromName("global");
    const stub = env.COUNTER.get(id);

    const doUrl = new URL("https://do/increment");
    doUrl.searchParams.set("day", dateStr);
    doUrl.searchParams.set("week", weekKey);

    const doResp = await stub.fetch(doUrl.toString());
    const data = await doResp.text();

    return new Response(data, {
      headers: { "Content-Type": "application/json", ...corsHeaders },
    });
  },
};

function isoWeekKey(dateStr) {
  const [y, m, d] = dateStr.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d));
  const dayNum = (date.getUTCDay() + 6) % 7;
  date.setUTCDate(date.getUTCDate() - dayNum + 3);
  const firstThursday = new Date(Date.UTC(date.getUTCFullYear(), 0, 4));
  const firstDayNum = (firstThursday.getUTCDay() + 6) % 7;
  firstThursday.setUTCDate(firstThursday.getUTCDate() - firstDayNum + 3);
  const week = 1 + Math.round((date.getTime() - firstThursday.getTime()) / (7 * 24 * 3600 * 1000));
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
}

export class VisitCounterDO {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request) {
    const url = new URL(request.url);
    const dayParam = "day:" + url.searchParams.get("day");
    const weekParam = "week:" + url.searchParams.get("week");

    const seeded = await this.state.storage.get("seeded");
    if (!seeded) {
      await this.state.storage.put({
        total: 113,
        [weekParam]: 113,
        [dayParam]: 113,
        seeded: true,
      });
    }

    let total = (await this.state.storage.get("total")) || 0;
    let day = (await this.state.storage.get(dayParam)) || 0;
    let week = (await this.state.storage.get(weekParam)) || 0;

    total += 1;
    day += 1;
    week += 1;

    await this.state.storage.put({
      total,
      [dayParam]: day,
      [weekParam]: week,
    });

    return new Response(JSON.stringify({ total, week, day }), {
      headers: { "Content-Type": "application/json" },
    });
  }
}
