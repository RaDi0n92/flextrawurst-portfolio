import { CANONICAL_ENTITY_IDS } from "../entities/seed_entities.ts";

export type ForumImportSourceType =
  | "flarum_export"
  | "html_archive"
  | "json_export"
  | "manual_fixture";

export interface ForumAccountCandidate {
  account_id: string;
  display_name: string;
  canonical_match: boolean;
  matched_slot_id: string | null;
}

export interface ForumDiscussionCandidate {
  discussion_id: string;
  title: string;
  created_at: string;
  post_ids: string[];
}

export interface ForumPostCandidate {
  post_id: string;
  discussion_id: string;
  author_account_id: string;
  created_at: string;
  content_text: string;
}

export interface ForumImportBundle {
  bundle_id: string;
  source_type: ForumImportSourceType;
  source_label: string;
  accounts: ForumAccountCandidate[];
  discussions: ForumDiscussionCandidate[];
  posts: ForumPostCandidate[];
}

export function createForumImportFixtureForCanonicalSlots(): ForumImportBundle {
  const accounts: ForumAccountCandidate[] = CANONICAL_ENTITY_IDS.map((id) => ({
    account_id: id,
    display_name: `Namenlos ${id}`,
    canonical_match: true,
    matched_slot_id: id,
  }));

  const discussions: ForumDiscussionCandidate[] = [
    {
      discussion_id: "disc-fixture-001",
      title: "Erste Weltdiskussion (Fixture)",
      created_at: "2026-01-01T00:00:00.000Z",
      post_ids: [
        "post-fixture-001",
        "post-fixture-002",
        "post-fixture-003",
      ],
    },
    {
      discussion_id: "disc-fixture-002",
      title: "Zweite Weltdiskussion (Fixture)",
      created_at: "2026-01-02T00:00:00.000Z",
      post_ids: [
        "post-fixture-004",
        "post-fixture-005",
        "post-fixture-006",
      ],
    },
  ];

  const posts: ForumPostCandidate[] = [
    {
      post_id: "post-fixture-001",
      discussion_id: "disc-fixture-001",
      author_account_id: "Schorschel",
      created_at: "2026-01-01T00:01:00.000Z",
      content_text: "Fixture-Post von Schorschel.",
    },
    {
      post_id: "post-fixture-002",
      discussion_id: "disc-fixture-001",
      author_account_id: "Resonanzknoten",
      created_at: "2026-01-01T00:02:00.000Z",
      content_text: "Fixture-Post von Resonanzknoten.",
    },
    {
      post_id: "post-fixture-003",
      discussion_id: "disc-fixture-001",
      author_account_id: "F3INSCHM3CK3R",
      created_at: "2026-01-01T00:03:00.000Z",
      content_text: "Fixture-Post von F3INSCHM3CK3R.",
    },
    {
      post_id: "post-fixture-004",
      discussion_id: "disc-fixture-002",
      author_account_id: "träumerlie",
      created_at: "2026-01-02T00:01:00.000Z",
      content_text: "Fixture-Post von träumerlie.",
    },
    {
      post_id: "post-fixture-005",
      discussion_id: "disc-fixture-002",
      author_account_id: "R1ZZ1",
      created_at: "2026-01-02T00:02:00.000Z",
      content_text: "Fixture-Post von R1ZZ1.",
    },
    {
      post_id: "post-fixture-006",
      discussion_id: "disc-fixture-002",
      author_account_id: "jumpa",
      created_at: "2026-01-02T00:03:00.000Z",
      content_text: "Fixture-Post von jumpa.",
    },
  ];

  return {
    bundle_id: "bundle-canonical-fixture-001",
    source_type: "manual_fixture",
    source_label: "Kanonische Fixture für sechs namelessAI-Slots",
    accounts,
    discussions,
    posts,
  };
}
