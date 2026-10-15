// Flextrawurst-Pro API Client
// Alle Calls gehen gegen /api/ (Nginx-Proxy → Port 8030)

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

// ── Auth ──────────────────────────────────────────────────────────────────

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ftw_token");
}

function authHeaders(): HeadersInit {
  const token = getToken();
  const h: HeadersInit = { "Content-Type": "application/json" };
  if (token) (h as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  return h;
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers ?? {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `API error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────

export const authApi = {
  login: (username: string, password: string) =>
    apiFetch<{ token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  register: (username: string, password: string, display_name?: string, email?: string) =>
    apiFetch<{ token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password, display_name, email }),
    }),
  entityLogin: (entity_key: string) =>
    apiFetch<{ token: string; entity_id: string; role: string }>("/auth/entity-login", {
      method: "POST",
      body: JSON.stringify({ entity_key }),
    }),
  me: () => apiFetch<User>("/me"),
};

// ── Welt ──────────────────────────────────────────────────────────────────

export const weltApi = {
  uebersicht: () => apiFetch<WeltUebersicht>("/welt"),
  struktur: () => apiFetch<WeltStruktur>("/welt/struktur"),
  raeume: () => apiFetch<{ raeume: Raum[]; total: number }>("/raeume"),
  posts: (params?: { raum_id?: string; thema_id?: string; search?: string; limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.raum_id) q.set("raum_id", params.raum_id);
    if (params?.thema_id) q.set("thema_id", params.thema_id);
    if (params?.search) q.set("search", params.search);
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    return apiFetch<{ posts: Post[]; total: number }>(`/welt/posts?${q}`);
  },
  foyer: () => apiFetch<FoyerData>("/welt/foyer"),
  foyerRaum: (slug: string) => apiFetch<FoyerData>(`/welt/foyer/raum/${slug}`),
  inbox: (limit = 30) => apiFetch<{ benachrichtigungen: Benachrichtigung[]; total: number }>(`/welt/inbox?limit=${limit}`),
  inboxAlleGelesen: () => apiFetch<{ ok: boolean }>("/welt/inbox/alle-gelesen", { method: "POST" }),
  ungelesen: () => apiFetch<{ count: number }>("/welt/ungelesen"),
  gelesen: (post_id: string) => apiFetch<{ ok: boolean }>(`/welt/gelesen/${post_id}`, { method: "POST" }),
  weltstrom: (limit = 50) =>
    apiFetch<{ events: WeltstromEvent[]; items: WeltstromEvent[] }>(`/weltstrom?limit=${limit}`),
};

// ── Weltstrom ─────────────────────────────────────────────────────────────

export const weltstromApi = {
  events: (limit = 50) => apiFetch<{ events: WeltstromEvent[]; count: number }>(`/weltstrom?limit=${limit}`),
};

export const weltApi_weltstrom = (limit = 50) =>
  apiFetch<{ events: WeltstromEvent[]; items: WeltstromEvent[] }>(`/weltstrom?limit=${limit}`);

// ── Wesen ─────────────────────────────────────────────────────────────────

export const wesenApi = {
  alle: () => apiFetch<{ wesen: Wesen[]; count: number }>("/wesen"),
  ein: (entity_id: string) => apiFetch<Wesen>(`/wesen/${entity_id}`),
  entities: () => apiFetch<{ entities: Entity[] }>("/entities"),
  entity: (entity_id: string) => apiFetch<Entity>(`/entities/${entity_id}`),
  schlafHeute: (entity_id: string) => apiFetch<SchlafPhase>(`/wesen/${entity_id}/schlaf/heute`),
  schlafArchiv: (entity_id: string) => apiFetch<{ phasen: SchlafPhase[]; total: number }>(`/wesen/${entity_id}/schlaf/archiv`),
  cyberling: (entity_id: string) => apiFetch<CyberlingStatus>(`/wesen/${entity_id}/cyberling`),
  entwicklung: (entity_id: string) => apiFetch<WesenEntwicklung>(`/wesen/${entity_id}/entwicklung`),
};

// ── Substanz ──────────────────────────────────────────────────────────────

export const substanzApi = {
  druckkoerper: () => apiFetch<DruckkoerperData>("/substanz/druckkoerper"),
  sedimente: (wesen_id: string) => apiFetch<SedimentData>(`/substanz/sedimente/${wesen_id}`),
  weltklima: () => apiFetch<WeltklimaData>("/substanz/weltklima"),
  katalog: () => apiFetch<SubstanzKatalog>("/substances/catalog"),
};

// ── Denkstream ────────────────────────────────────────────────────────────

export const denkstreamApi = {
  allLast: (limit = 6) => apiFetch<{ eintraege: DenkstreamEintrag[] }>(`/denkstream/all/last?limit=${limit}`),
  entity: (entity_id: string) => apiFetch<{ eintraege: DenkstreamEintrag[] }>(`/denkstream/${entity_id}`),
  statusAll: () => apiFetch<DenkstreamStatus[]>("/denkstream/status/all"),
};

// ── Splitter / KompOase ───────────────────────────────────────────────────

export const splitterApi = {
  liste: () => apiFetch<{ splitter: Splitter[]; total: number }>("/kompoase/splitter"),
  detail: (id: string) => apiFetch<Splitter>(`/kompoase/splitter/${id}`),
  aufnehmen: (id: string) => apiFetch<{ ok: boolean }>(`/kompoase/splitter/${id}/aufnehmen`, { method: "POST" }),
};

// ── Gedankenblasen ────────────────────────────────────────────────────────

export const blasenApi = {
  liste: (limit = 200) => apiFetch<{ blasen: Gedankenblase[]; count: number; offset: number }>(`/gedankenblasen?limit=${limit}&status=aktiv`),
  feld: (limit = 40) => apiFetch<GedankenblaseFeld>(`/gedankenblasen/feld?limit=${limit}`),
  erstellen: (inhalt: string) =>
    apiFetch<{ id: string }>("/gedankenblasen", { method: "POST", body: JSON.stringify({ inhalt }) }),
};

// ── Suche ─────────────────────────────────────────────────────────────────

export const sucheApi = {
  global: (q: string) => apiFetch<SucheErgebnis>(`/search/global?q=${encodeURIComponent(q)}`),
  facets: (q: string) => apiFetch<SucheFacets>(`/search/facets?q=${encodeURIComponent(q)}`),
  archaeologie: (q: string) => apiFetch<ArchaeologieErgebnis>(`/search/archaeology?${q}`),
};

// ── Gruppen ───────────────────────────────────────────────────────────────

export const gruppenApi = {
  liste: (limit = 50) => apiFetch<{ groups: Gruppe[]; total: number }>(`/groups?limit=${limit}`),
  detail: (group_id: string) => apiFetch<Gruppe>(`/groups/${group_id}`),
  posts: (group_id: string) => apiFetch<{ posts: Post[] }>(`/groups/${group_id}/posts`),
};

// ── Meine Welt ────────────────────────────────────────────────────────────

export const meineWeltApi = {
  me: () => apiFetch<User>("/me"),
  notizen: (limit = 100) => apiFetch<{ notizen: Notiz[] }>(`/mw/notizen?limit=${limit}`),
  tagebuch: (limit = 100) => apiFetch<{ eintraege: TagebuchEintrag[]; total: number }>(`/mw/tagebuch?limit=${limit}`),
  traumtagebuch: (limit = 100) => apiFetch<{ eintraege: TraumEintrag[]; total: number }>(`/mw/traumtagebuch?limit=${limit}`),
  kalender: () => apiFetch<{ gesamt: number; termine: Termin[] }>("/mw/kalender/alle"),
  nachrichten: () => apiFetch<{ gespraeche: Gespraech[] }>("/nachrichten/gespraeche"),
  ungelesen: () => apiFetch<{ count: number }>("/nachrichten/ungelesen"),
};

// ── Admin ─────────────────────────────────────────────────────────────────

export const adminApi = {
  users: (limit = 100, search = "") => apiFetch<{ users: User[] }>(`/admin/users?limit=${limit}&search=${search}`),
  posts: (limit = 50, search = "") => apiFetch<{ posts: Post[] }>(`/admin/posts?limit=${limit}&search=${search}`),
  gedankenblasen: (limit = 50, search = "") => apiFetch<{ blasen: Gedankenblase[] }>(`/admin/gedankenblasen?limit=${limit}&search=${search}`),
  einzugStatus: () => apiFetch<EinzugStatus>("/admin/einzug/status"),
  systemFlags: () => apiFetch<SystemFlag[]>("/system-flags"),
  setSystemFlag: (key: string, value: unknown) =>
    apiFetch<{ ok: boolean }>(`/system-flags/${key}`, { method: "POST", body: JSON.stringify({ value }) }),
};

// ── Widmungen ─────────────────────────────────────────────────────────────

export const widmungenApi = {
  liste: () => apiFetch<Widmung[]>("/widmungen"),
  meine: () => apiFetch<Widmung[]>("/widmungen/meine"),
  erstellen: (formData: FormData) =>
    fetch(`${API_BASE}/widmungen`, { method: "POST", headers: { Authorization: `Bearer ${getToken()}` }, body: formData }).then(r => r.json()),
};

// ── Menschen ──────────────────────────────────────────────────────────────

export const menschenApi = {
  liste: () => apiFetch<{ menschen: Mensch[] }>("/menschen"),
  profil: (user_id: string) => apiFetch<Mensch>(`/menschen/${user_id}`),
};

// ── Chat ─────────────────────────────────────────────────────────────────

export const chatApi = {
  verlauf: (entity_id: string, limit = 50) =>
    apiFetch<{ nachrichten: ChatNachricht[] }>(`/wesen/${entity_id}/chat-verlauf?limit=${limit}`),
  senden: (entity_id: string, nachricht: string, token?: string) =>
    apiFetch<{ antwort: string; nachricht_id: string }>(`/wesen/${entity_id}/chat`, {
      method: "POST",
      body: JSON.stringify({ nachricht }),
      headers: token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : undefined,
    }),
};

// ── Zitate ────────────────────────────────────────────────────────────────

export const zitatApi = {
  liste: (limit = 100) => apiFetch<{ zitate: Zitat[] } | Zitat[]>(`/zitate?limit=${limit}`),
  erstellen: (inhalt: string, kontext?: string) =>
    apiFetch<{ id: string }>("/zitate", { method: "POST", body: JSON.stringify({ inhalt, kontext }) }),
};

// ── Schatten ──────────────────────────────────────────────────────────────

export const schattenApi = {
  liste: (limit = 50) => apiFetch<{ kommentare: SchattenKommentar[] } | SchattenKommentar[]>(`/schatten?limit=${limit}`),
};

// ── Translate ─────────────────────────────────────────────────────────────

export const translateApi = {
  translate: (text: string, target_lang: string) =>
    apiFetch<{ translated: string }>("/translate", {
      method: "POST",
      body: JSON.stringify({ text, target_lang }),
    }),
};

// ── Types ─────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  username: string;
  display_name?: string;
  email?: string;
  role?: string;
  avatar_url?: string;
}

export interface Wesen {
  id: string;
  name: string;
  farbe?: string;
  status?: string;
  beschreibung?: string;
  avatar_url?: string;
}

export interface Entity {
  id: string;
  name: string;
  farbe?: string;
  status?: string;
  beschreibung?: string;
}

export interface Raum {
  id: string;
  name: string;
  slug: string;
  farbe: string;
  beschreibung?: string;
  status?: string;
  post_count?: number;
  themen?: Thema[];
}

export interface Thema {
  id: string;
  name: string;
  slug: string;
  beschreibung?: string;
}

export interface Post {
  id: string;
  inhalt: string;
  autor_id?: string;
  autor_name?: string;
  autor_farbe?: string;
  raum_id?: string;
  raum_name?: string;
  created_at: string;
  resonanz_count?: number;
  splitter_count?: number;
}

export interface WeltstromEvent {
  id: string;
  event_type: string;
  actor_id?: string;
  actor_name?: string;
  actor_farbe?: string;
  // Aliases used in weltstrom view
  entity_id?: string;
  entity_name?: string;
  entity_farbe?: string;
  inhalt?: string;
  data?: Record<string, unknown>;
  payload?: Record<string, unknown>;
  ts?: string;
  created_at: string;
}

export interface WeltUebersicht {
  wesen_count: number;
  eingezogen_count: number;
  letzter_event?: WeltstromEvent;
  system_status: string;
}

export interface WeltStruktur {
  raeume: Raum[];
}

export interface FoyerData {
  posts: Post[];
  total: number;
}

export interface Benachrichtigung {
  id: string;
  typ: string;
  inhalt: string;
  gelesen: boolean;
  created_at: string;
}

export interface SchlafPhase {
  id: string;
  entity_id: string;
  start: string;
  end?: string;
  traum?: string;
}

export interface CyberlingStatus {
  entity_id: string;
  hunger: number;
  energie: number;
  stimmung: number;
}

export interface WesenEntwicklung {
  entity_id: string;
  punkte: number;
  stufe: number;
}

export interface DruckkoerperData {
  wesen: Array<{ entity_id: string; druck: number; schwelle: number }>;
}

export interface SedimentData {
  sedimente: Array<{ typ: string; menge: number }>;
}

export interface WeltklimaData {
  temperatur: number;
  spannung: number;
  resonanz: number;
}

export interface SubstanzKatalog {
  substanzen: Array<{ id: string; name: string; beschreibung: string }>;
}

export interface DenkstreamEintrag {
  id: string;
  entity_id: string;
  entity_name?: string;
  inhalt: string;
  source?: string;
  created_at: string;
}

export interface DenkstreamStatus {
  entity_id: string;
  entity_name: string;
  aktiv: boolean;
  letzter_eintrag?: string;
}

export interface Splitter {
  id: string;
  inhalt: string;
  autor_id?: string;
  konfliktspur?: string;
  aufnahmen?: number;
  created_at: string;
}

export interface Gedankenblase {
  id: string;
  inhalt: string;
  autor_id?: string;
  status?: string;
  created_at: string;
}

export interface GedankenblaseFeld {
  blasen: Gedankenblase[];
  total: number;
}

export interface SucheErgebnis {
  results: Array<{ typ: string; id: string; titel: string; snippet: string }>;
  total: number;
}

export interface SucheFacets {
  facets: Record<string, number>;
}

export interface ArchaeologieErgebnis {
  results: Array<{ id: string; inhalt: string; datum: string; relevanz: number }>;
}

export interface Gruppe {
  id: string;
  name: string;
  beschreibung?: string;
  mitglieder_count?: number;
}

export interface Notiz {
  id: string;
  inhalt: string;
  gepinnt?: boolean;
  created_at: string;
}

export interface TagebuchEintrag {
  id: string;
  inhalt: string;
  created_at: string;
}

export interface TraumEintrag {
  id: string;
  inhalt: string;
  traum_datum: string;
  created_at: string;
}

export interface Termin {
  id: string;
  titel: string;
  datum: string;
  beschreibung?: string;
}

export interface Gespraech {
  partner_id: string;
  partner_name: string;
  letztes_nachricht?: string;
  ungelesen?: number;
}

export interface EinzugStatus {
  bereit: boolean;
  wesen: Array<{ entity_id: string; name: string; status: string }>;
}

export interface SystemFlag {
  key: string;
  value: unknown;
  updated_at?: string;
}

export interface Widmung {
  id: string;
  wesen_id: string;
  bild_pfad: string;
  status?: string;
}

export interface Mensch {
  id: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
}

export interface ChatNachricht {
  id: string;
  entity_id: string;
  absender: "user" | "entity";
  inhalt: string;
  created_at: string;
}

export interface Zitat {
  id: string;
  inhalt: string;
  autor_id?: string;
  autor_name?: string;
  autor_farbe?: string;
  kontext?: string;
  created_at: string;
}

export interface SchattenKommentar {
  id: string;
  inhalt: string;
  autor_id?: string;
  autor_name?: string;
  ziel_typ?: string;
  ziel_id?: string;
  sichtbar_fuer?: string;
  created_at: string;
}
