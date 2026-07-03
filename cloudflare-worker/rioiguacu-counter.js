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

    // Data local de Brasília, no formato YYYY-MM-DD.
    const dateStr = new Intl.DateTimeFormat("en-CA", {
      timeZone: "America/Sao_Paulo",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date());

    const weekKey = isoWeekKey(dateStr);

    // Um único Durable Object global cuida de todo o incremento: como o
    // runtime do Cloudflare processa as requisições de um mesmo Durable
    // Object em sequência (nunca em paralelo), não existe mais a corrida
    // que corrompia os números no Workers KV (onde "hoje" podia ficar
    // maior que "na semana", por exemplo).
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
  const dayNum = (date.getUTCDay() + 6) % 7; // 0 = segunda-feira
  date.setUTCDate(date.getUTCDate() - dayNum + 3); // quinta-feira da semana ISO
  const firstThursday = new Date(Date.UTC(date.getUTCFullYear(), 0, 4));
  const firstDayNum = (firstThursday.getUTCDay() + 6) % 7;
  firstThursday.setUTCDate(firstThursday.getUTCDate() - firstDayNum + 3);
  const week = 1 + Math.round((date.getTime() - firstThursday.getTime()) / (7 * 24 * 3600 * 1000));
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
}

// Durable Object responsável por guardar e incrementar os contadores.
// Cada chamada a este objeto é processada de forma isolada e em ordem
// pelo próprio runtime do Cloudflare (garantia da plataforma), então a
// leitura + soma + gravação abaixo é efetivamente atômica, sem depender
// de nenhum lock manual.
export class VisitCounterDO {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request) {
    const url = new URL(request.url);
    const dayParam = "day:" + url.searchParams.get("day");
    const weekParam = "week:" + url.searchParams.get("week");

    // Migração única: na primeira vez que este Durable Object for usado
    // (armazenamento ainda vazio), começa a contagem a partir dos últimos
    // números vistos no sistema antigo (Workers KV), em vez de voltar a
    // zero e perder o histórico de visitas já registrado.
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
