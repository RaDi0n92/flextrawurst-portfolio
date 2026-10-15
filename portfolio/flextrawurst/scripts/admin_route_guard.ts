import type { IncomingHttpHeaders } from "node:http";

const ADMIN_PREFIXES = [
  "/wesen", "/api/wesen-dienst-wizard", "/api/flarumstyler",
  "/dolphin", "/aufgabenchats",
];

export function requiresAdministrativeAuth(url: string, method: string): boolean {
  const path = url.split("?", 1)[0];
  // Match the existing nginx prefix, including /api/flarumstyler_verlauf.
  // Its reads were already protected by Basic and must not become public.
  if (path.startsWith("/api/flarumstyler") && method !== "OPTIONS") return true;
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return false;
  return ADMIN_PREFIXES.some(prefix => path === prefix || path.startsWith(prefix + "/"));
}

// Defense in depth: reject cross-site administrative writes before dispatch.
// Non-browser automation still needs explicit authentication; loopback is not exempt.
export function permitsAdministrativeOrigin(headers: IncomingHttpHeaders): boolean {
  const site = headers["sec-fetch-site"];
  if (site && site !== "same-origin" && site !== "none") return false;
  const origin = headers.origin;
  if (origin === undefined) return true;
  if (typeof origin !== "string" || !headers.host) return false;
  try {
    const parsed = new URL(origin);
    return ["http:", "https:"].includes(parsed.protocol)
      && parsed.origin === origin && parsed.host === headers.host;
  } catch { return false; }
}

export async function administrativeAuthStatus(
  headers: IncomingHttpHeaders,
  fetcher: typeof fetch = fetch,
): Promise<number> {
  const token = headers.authorization;
  if (typeof token !== "string" || !/^Bearer \S+$/.test(token)) return 401;
  try {
    // Fixed local verifier, no redirects, no Basic fallback or caller-selected URL.
    const response = await fetcher("http://127.0.0.1:8030/auth/admin-check", {
      headers: { Authorization: token }, redirect: "error",
      signal: AbortSignal.timeout(3000),
    });
    if (response.status === 401 || response.status === 403) return response.status;
    if (response.status !== 200) return 503;
    return (await response.json()).ok === true ? 200 : 503;
  } catch { return 503; }
}

export function withAdministrativeClient(html: string): string {
  return html.replace(/<head\b[^>]*>/i, match => match + '<script src="/admin-auth-client.js"></script>');
}
