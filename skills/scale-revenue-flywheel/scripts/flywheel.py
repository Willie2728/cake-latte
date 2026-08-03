#!/usr/bin/env python3
"""Local control plane for the Revenue Flywheel skill.

Uses only the Python standard library. External publishing is dry-run unless
an approved publisher command is given `--execute` and all approval checks pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS content (
  content_id TEXT PRIMARY KEY,
  fingerprint TEXT NOT NULL UNIQUE,
  platform TEXT NOT NULL,
  format TEXT NOT NULL,
  audience TEXT NOT NULL,
  problem TEXT NOT NULL,
  hypothesis TEXT NOT NULL,
  experiment_cell TEXT NOT NULL,
  hook TEXT NOT NULL,
  body_json TEXT NOT NULL,
  caption TEXT NOT NULL,
  cta TEXT NOT NULL,
  media_json TEXT NOT NULL,
  disclosure TEXT NOT NULL,
  rights_confirmed INTEGER NOT NULL,
  destination_url TEXT NOT NULL,
  status TEXT NOT NULL,
  scheduled_at TEXT,
  approved_at TEXT,
  approved_by TEXT,
  created_at TEXT NOT NULL,
  risk_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS publications (
  publication_id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  external_post_id TEXT NOT NULL,
  external_url TEXT,
  integration_id TEXT,
  payload_hash TEXT,
  state TEXT NOT NULL,
  published_at TEXT NOT NULL,
  UNIQUE(platform, external_post_id),
  FOREIGN KEY(content_id) REFERENCES content(content_id)
);

CREATE TABLE IF NOT EXISTS metrics (
  content_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  impressions INTEGER NOT NULL DEFAULT 0,
  views INTEGER NOT NULL DEFAULT 0,
  average_watch_pct REAL NOT NULL DEFAULT 0,
  completion_rate REAL NOT NULL DEFAULT 0,
  shares INTEGER NOT NULL DEFAULT 0,
  saves INTEGER NOT NULL DEFAULT 0,
  comments INTEGER NOT NULL DEFAULT 0,
  profile_visits INTEGER NOT NULL DEFAULT 0,
  link_clicks INTEGER NOT NULL DEFAULT 0,
  signups INTEGER NOT NULL DEFAULT 0,
  trials INTEGER NOT NULL DEFAULT 0,
  purchases INTEGER NOT NULL DEFAULT 0,
  new_mrr REAL NOT NULL DEFAULT 0,
  one_time_revenue REAL NOT NULL DEFAULT 0,
  refunds REAL NOT NULL DEFAULT 0,
  content_cost REAL NOT NULL DEFAULT 0,
  PRIMARY KEY(content_id, platform, captured_at),
  FOREIGN KEY(content_id) REFERENCES content(content_id)
);

CREATE TABLE IF NOT EXISTS learnings (
  learning_id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  scope TEXT NOT NULL,
  summary TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  action TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  job TEXT NOT NULL,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  state TEXT NOT NULL,
  detail_json TEXT NOT NULL
);
"""


DEFAULT_RISK_PHRASES = (
    "guaranteed income",
    "guaranteed virality",
    "risk-free",
    "get rich quick",
    "instant wealth",
    "no effort required",
)


class FlywheelError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:64] or "campaign"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FlywheelError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FlywheelError(f"Invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def workspace_paths(workspace: str | Path) -> tuple[Path, Path, Path]:
    root = Path(workspace).expanduser().resolve()
    return root, root / "campaign.json", root / "flywheel.sqlite3"


def load_campaign(workspace: str | Path) -> tuple[Path, dict[str, Any], Path]:
    root, config_path, db_path = workspace_paths(workspace)
    config = load_json(config_path)
    if config.get("version") != 1:
        raise FlywheelError("Unsupported campaign version; expected version 1")
    return root, config, db_path


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def platform_config(config: dict[str, Any], platform: str) -> dict[str, Any]:
    for item in config.get("platforms", []):
        if str(item.get("name", "")).lower() == platform.lower():
            return item
    raise FlywheelError(f"Platform is not configured: {platform}")


def build_destination_url(base_url: str, campaign_id: str, platform: str, content_id: str) -> str:
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise FlywheelError("offer.landing_url must be an absolute HTTP(S) URL")
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.extend(
        [
            ("utm_source", platform),
            ("utm_medium", "organic_social"),
            ("utm_campaign", campaign_id),
            ("utm_content", content_id),
        ]
    )
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment)
    )


def content_fingerprint(item: dict[str, Any]) -> str:
    normalized = {
        "platform": str(item.get("platform", "")).strip().lower(),
        "format": str(item.get("format", "")).strip().lower(),
        "hook": re.sub(r"\s+", " ", str(item.get("hook", "")).strip().lower()),
        "body": item.get("body", []),
        "cta": re.sub(r"\s+", " ", str(item.get("cta", "")).strip().lower()),
    }
    encoded = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def content_risks(item: dict[str, Any], config: dict[str, Any]) -> list[str]:
    blob = " ".join(
        [
            str(item.get("hook", "")),
            str(item.get("caption", "")),
            str(item.get("cta", "")),
            json.dumps(item.get("body", []), ensure_ascii=False),
        ]
    ).lower()
    prohibited = [str(x).lower() for x in config.get("brand", {}).get("prohibited_claims", [])]
    risks = [f"prohibited claim phrase: {phrase}" for phrase in (*DEFAULT_RISK_PHRASES, *prohibited) if phrase and phrase in blob]
    guardrails = config.get("guardrails", {})
    if guardrails.get("require_rights_confirmation", True) and not item.get("rights_confirmed", False):
        risks.append("media rights are not confirmed")
    if guardrails.get("require_synthetic_media_disclosure", True) and not str(item.get("disclosure", "")).strip():
        risks.append("synthetic/commercial disclosure is missing")
    return sorted(set(risks))


def required_text(item: dict[str, Any], keys: Iterable[str]) -> None:
    missing = [key for key in keys if not str(item.get(key, "")).strip()]
    if missing:
        raise FlywheelError(f"Content item is missing required fields: {', '.join(missing)}")


def command_init(args: argparse.Namespace) -> None:
    root, config_path, db_path = workspace_paths(args.workspace)
    if config_path.exists() and not args.force:
        raise FlywheelError(f"Campaign already exists: {config_path}; use --force to replace the config")
    root.mkdir(parents=True, exist_ok=True)
    campaign_id = slugify(f"{args.business}-{args.offer}")
    target_date = (datetime.now(timezone.utc) + timedelta(days=args.target_days)).date().isoformat()
    config = {
        "version": 1,
        "campaign_id": campaign_id,
        "business": {"name": args.business, "timezone": args.timezone},
        "goal": {
            "current_mrr": args.current_mrr,
            "target_mrr": args.target_mrr,
            "target_date": target_date,
            "average_revenue_per_customer": args.arpu,
            "monthly_churn_rate": args.churn,
            "gross_margin_rate": args.gross_margin,
        },
        "offer": {
            "name": args.offer,
            "type": "subscription",
            "landing_url": args.landing_url,
            "stripe_payment_link": "",
            "primary_cta": "Start now",
        },
        "audience": {
            "primary": "REPLACE: initial narrow audience",
            "problem": "REPLACE: costly or urgent problem",
            "desired_outcome": "REPLACE: valued result",
        },
        "brand": {
            "voice": ["clear", "credible", "human"],
            "must_include": [],
            "prohibited_claims": ["guaranteed income", "guaranteed virality"],
        },
        "platforms": [
            {"name": "tiktok", "integration_id": "", "daily_cap": 2, "publishing_mode": "review_required", "default_post_time": "10:30"},
            {"name": "instagram", "integration_id": "", "daily_cap": 2, "publishing_mode": "review_required", "default_post_time": "11:15"},
            {"name": "youtube", "integration_id": "", "daily_cap": 1, "publishing_mode": "review_required", "default_post_time": "12:00"},
        ],
        "experimentation": {
            "allocation": {"exploit": 0.6, "explore": 0.2, "challenger": 0.2},
            "minimum_views_for_attention_decision": 1000,
            "minimum_clicks_for_conversion_decision": 50,
            "minimum_purchases_for_revenue_decision": 3,
        },
        "guardrails": {
            "require_rights_confirmation": True,
            "require_synthetic_media_disclosure": True,
            "allow_automated_comments": False,
            "allow_automated_direct_messages": False,
            "allow_paid_spend": False,
            "daily_cost_limit": 25,
        },
        "connectors": {
            "primary_model": "gpt-5.6-sol",
            "fallback_models": [],
            "publisher": "blotato",
            "publisher_fallback": "postiz",
            "web_research": "firecrawl",
            "commerce": "stripe",
            "required_environment": ["OPENAI_API_KEY", "BLOTATO_API_KEY", "FIRECRAWL_API_KEY", "STRIPE_SECRET_KEY"],
        },
    }
    write_json(config_path, config)
    with connect(db_path) as connection:
        connection.execute(
            "INSERT INTO runs(job, started_at, completed_at, state, detail_json) VALUES(?,?,?,?,?)",
            ("init", utc_now(), utc_now(), "complete", json.dumps({"campaign_id": campaign_id})),
        )
    (root / "evidence").mkdir(exist_ok=True)
    (root / "media").mkdir(exist_ok=True)
    (root / "exports").mkdir(exist_ok=True)
    emit({"campaign": str(config_path), "database": str(db_path), "campaign_id": campaign_id, "state": "initialized"})


def command_health(args: argparse.Namespace) -> None:
    root, config, db_path = load_campaign(args.workspace)
    issues: list[str] = []
    if not db_path.exists():
        issues.append("state database is missing")
    for field in ("primary", "problem", "desired_outcome"):
        if str(config.get("audience", {}).get(field, "")).startswith("REPLACE"):
            issues.append(f"audience.{field} is not configured")
    env_names = config.get("connectors", {}).get("required_environment", [])
    env_presence = {name: bool(os.environ.get(name)) for name in env_names}
    missing_env = [name for name, present in env_presence.items() if not present]
    if missing_env:
        issues.append("missing environment variables: " + ", ".join(missing_env))
    platform_health = []
    for item in config.get("platforms", []):
        platform_health.append(
            {
                "platform": item.get("name"),
                "publishing_mode": item.get("publishing_mode"),
                "integration_configured": bool(item.get("integration_id")),
                "daily_cap": item.get("daily_cap"),
            }
        )
    emit(
        {
            "workspace": str(root),
            "state": "ready" if not issues else "needs_configuration",
            "issues": issues,
            "environment_presence": env_presence,
            "platforms": platform_health,
        }
    )


def target_model(config: dict[str, Any]) -> dict[str, Any]:
    goal = config.get("goal", {})
    current = float(goal.get("current_mrr", 0))
    target = float(goal.get("target_mrr", 0))
    arpu = float(goal.get("average_revenue_per_customer", 0))
    churn = float(goal.get("monthly_churn_rate", 0))
    if target <= 0 or arpu <= 0 or not 0 <= churn < 1:
        raise FlywheelError("target_mrr and ARPU must be positive; churn must be between 0 and 1")
    target_date = datetime.fromisoformat(str(goal["target_date"])).date()
    today = datetime.now(timezone.utc).date()
    months = max(1, math.ceil(max(1, (target_date - today).days) / 30.4375))
    retained_current = current * ((1 - churn) ** months)
    annuity = sum((1 - churn) ** j for j in range(months))
    required_per_month = max(0, math.ceil((target - retained_current) / (arpu * annuity)))
    target_customers = math.ceil(target / arpu)
    return {
        "current_mrr": round(current, 2),
        "target_mrr": round(target, 2),
        "target_date": target_date.isoformat(),
        "months_to_target": months,
        "arpu": round(arpu, 2),
        "monthly_churn_rate": churn,
        "target_active_customers": target_customers,
        "modeled_new_customers_per_month": required_per_month,
        "modeled_new_customers_per_week": round(required_per_month / 4.345, 1),
        "disclaimer": "Planning model only; not a forecast or guarantee.",
    }


def command_model_target(args: argparse.Namespace) -> None:
    _, config, _ = load_campaign(args.workspace)
    emit(target_model(config))


def command_enqueue(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    source = load_json(Path(args.input).expanduser().resolve())
    items = source.get("items") if isinstance(source, dict) else source
    if not isinstance(items, list) or not items:
        raise FlywheelError("Input must contain a non-empty items array")
    inserted = []
    rejected = []
    with connect(db_path) as connection:
        for index, item in enumerate(items):
            try:
                if not isinstance(item, dict):
                    raise FlywheelError("item must be an object")
                required_text(
                    item,
                    ("platform", "format", "audience", "problem", "hypothesis", "experiment_cell", "hook", "caption", "cta"),
                )
                platform = str(item["platform"]).lower()
                platform_config(config, platform)
                fingerprint = content_fingerprint(item)
                content_id = f"{slugify(config['campaign_id'])}-{fingerprint[:12]}"
                risks = content_risks(item, config)
                destination = build_destination_url(
                    str(config["offer"]["landing_url"]), str(config["campaign_id"]), platform, content_id
                )
                connection.execute(
                    """
                    INSERT INTO content(
                      content_id,fingerprint,platform,format,audience,problem,hypothesis,experiment_cell,
                      hook,body_json,caption,cta,media_json,disclosure,rights_confirmed,destination_url,
                      status,scheduled_at,created_at,risk_json
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        content_id,
                        fingerprint,
                        platform,
                        str(item["format"]),
                        str(item["audience"]),
                        str(item["problem"]),
                        str(item["hypothesis"]),
                        str(item["experiment_cell"]),
                        str(item["hook"]),
                        json.dumps(item.get("body", []), ensure_ascii=False),
                        str(item["caption"]),
                        str(item["cta"]),
                        json.dumps(item.get("media", []), ensure_ascii=False),
                        str(item.get("disclosure", "")),
                        int(bool(item.get("rights_confirmed", False))),
                        destination,
                        "blocked" if risks else "draft",
                        item.get("scheduled_at"),
                        utc_now(),
                        json.dumps(risks, ensure_ascii=False),
                    ),
                )
                inserted.append({"content_id": content_id, "platform": platform, "status": "blocked" if risks else "draft", "risks": risks, "destination_url": destination})
            except (FlywheelError, sqlite3.IntegrityError) as exc:
                rejected.append({"index": index, "reason": "duplicate content" if isinstance(exc, sqlite3.IntegrityError) else str(exc)})
    emit({"inserted": inserted, "rejected": rejected})


def get_content(connection: sqlite3.Connection, content_id: str) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM content WHERE content_id=?", (content_id,)).fetchone()
    if not row:
        raise FlywheelError(f"Unknown content id: {content_id}")
    return row


def command_approve(args: argparse.Namespace) -> None:
    _, _, db_path = load_campaign(args.workspace)
    if not args.approved_by.strip():
        raise FlywheelError("--approved-by is required")
    with connect(db_path) as connection:
        row = get_content(connection, args.content_id)
        risks = json.loads(row["risk_json"])
        if risks:
            raise FlywheelError("Cannot approve blocked content: " + "; ".join(risks))
        if row["status"] not in {"draft", "approved"}:
            raise FlywheelError(f"Cannot approve content in state {row['status']}")
        connection.execute(
            "UPDATE content SET status='approved', approved_at=?, approved_by=? WHERE content_id=?",
            (utc_now(), args.approved_by.strip(), args.content_id),
        )
    emit({"content_id": args.content_id, "state": "approved", "approved_by": args.approved_by.strip()})


def command_queue(args: argparse.Namespace) -> None:
    _, _, db_path = load_campaign(args.workspace)
    query = "SELECT content_id,platform,format,experiment_cell,hook,status,scheduled_at,approved_by,destination_url FROM content"
    params: list[Any] = []
    conditions = []
    if args.status:
        conditions.append("status=?")
        params.append(args.status)
    if args.platform:
        conditions.append("platform=?")
        params.append(args.platform.lower())
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(args.limit)
    with connect(db_path) as connection:
        rows = [dict(row) for row in connection.execute(query, params).fetchall()]
    emit({"items": rows, "count": len(rows)})


def postiz_settings(platform: str, args: argparse.Namespace) -> dict[str, Any]:
    if platform == "tiktok":
        return {
            "__type": "tiktok",
            "title": args.title or "",
            "privacy_level": args.privacy_level,
            "duet": False,
            "stitch": False,
            "comment": True,
            "autoAddMusic": "no",
            "brand_content_toggle": bool(args.branded_content),
            "brand_organic_toggle": bool(args.brand_organic),
            "video_made_with_ai": True,
            "content_posting_method": "UPLOAD",
        }
    if platform == "youtube":
        return {
            "__type": "youtube",
            "title": args.title or "Short",
            "type": "short",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        }
    if platform == "instagram":
        return {"__type": "instagram-standalone", "post_type": "reel"}
    return {"__type": platform}


def build_postiz_payload(row: sqlite3.Row, integration_id: str, args: argparse.Namespace) -> dict[str, Any]:
    if row["status"] != "approved":
        raise FlywheelError(f"Content must be approved before payload creation; current state is {row['status']}")
    media = json.loads(row["media_json"])
    if not media:
        raise FlywheelError("Content has no media references")
    text = f"{row['caption']}\n\n{row['cta']}: {row['destination_url']}"
    scheduled_at = row["scheduled_at"]
    return {
        "type": "schedule" if scheduled_at else "now",
        "date": scheduled_at or utc_now(),
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": {"id": integration_id},
                "value": [{"content": text, "image": media}],
                "settings": postiz_settings(str(row["platform"]), args),
            }
        ],
    }


def command_postiz_payload(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    with connect(db_path) as connection:
        row = get_content(connection, args.content_id)
        integration_id = args.integration_id or platform_config(config, row["platform"]).get("integration_id")
        if not integration_id:
            raise FlywheelError("A Postiz integration id is required")
        emit(build_postiz_payload(row, str(integration_id), args))


def command_postiz_send(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    if not args.execute:
        raise FlywheelError("External publishing is disabled without --execute")
    if not args.approved_by.strip():
        raise FlywheelError("--approved-by is required for publication")
    api_key = os.environ.get("POSTIZ_API_KEY")
    if not api_key:
        raise FlywheelError("POSTIZ_API_KEY is not set")
    base_url = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com/public/v1").rstrip("/")
    with connect(db_path) as connection:
        row = get_content(connection, args.content_id)
        if row["approved_by"] != args.approved_by.strip():
            raise FlywheelError("--approved-by must match the recorded content approval")
        pconfig = platform_config(config, row["platform"])
        mode = pconfig.get("publishing_mode", "review_required")
        if mode == "draft_only":
            raise FlywheelError("Platform publishing mode is draft_only")
        integration_id = args.integration_id or pconfig.get("integration_id")
        if not integration_id:
            raise FlywheelError("A Postiz integration id is required")
        payload = build_postiz_payload(row, str(integration_id), args)
        payload_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        request = urllib.request.Request(
            f"{base_url}/posts",
            data=payload_bytes,
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
            raise FlywheelError(f"Postiz returned HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise FlywheelError(f"Postiz request failed: {exc.reason}") from exc
        first = result[0] if isinstance(result, list) and result else result if isinstance(result, dict) else {}
        post_id = str(first.get("postId") or first.get("id") or "")
        if not post_id:
            raise FlywheelError("Postiz response did not include a post id; publication state is ambiguous")
        connection.execute(
            """INSERT INTO publications(content_id,platform,external_post_id,external_url,integration_id,payload_hash,state,published_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (args.content_id, row["platform"], post_id, first.get("url"), integration_id, payload_hash, "submitted", utc_now()),
        )
        connection.execute("UPDATE content SET status='published' WHERE content_id=?", (args.content_id,))
    emit({"content_id": args.content_id, "platform": row["platform"], "post_id": post_id, "state": "submitted"})


def blotato_target(platform: str, args: argparse.Namespace) -> dict[str, Any]:
    target: dict[str, Any] = {"targetType": platform}
    if platform == "tiktok":
        target.update({
            "privacyLevel": args.privacy_level,
            "disabledComments": bool(args.disabled_comments),
            "disabledDuet": bool(args.disabled_duet),
            "disabledStitch": bool(args.disabled_stitch),
            "isBrandedContent": bool(args.branded_content),
            "isYourBrand": bool(args.your_brand),
            "isAiGenerated": not bool(args.not_ai_generated),
            "isDraft": bool(args.is_draft),
        })
    elif platform == "youtube":
        target.update({
            "title": args.title or "Short",
            "privacyStatus": args.youtube_privacy,
            "shouldNotifySubscribers": bool(args.notify_subscribers),
            "isMadeForKids": False,
            "containsSyntheticMedia": not bool(args.not_ai_generated),
        })
    elif platform == "instagram":
        target["mediaType"] = args.media_type
    elif platform in {"facebook", "linkedin"}:
        if platform == "facebook" and not args.page_id:
            raise FlywheelError("--page-id is required for Facebook publishing")
        if args.page_id:
            target["pageId"] = args.page_id
    elif platform == "pinterest":
        if not args.board_id:
            raise FlywheelError("--board-id is required for Pinterest publishing")
        target["boardId"] = args.board_id
        if args.title:
            target["title"] = args.title
    return target


def build_blotato_payload(row: sqlite3.Row, account_id: str, args: argparse.Namespace) -> dict[str, Any]:
    if row["status"] != "approved":
        raise FlywheelError(f"Content must be approved before payload creation; current state is {row['status']}")
    raw_media = json.loads(row["media_json"])
    media_urls = [item.get("path") if isinstance(item, dict) else item for item in raw_media]
    media_urls = [str(url) for url in media_urls if url]
    if not media_urls:
        raise FlywheelError("Content has no media URLs")
    if any(not url.startswith(("https://", "http://")) for url in media_urls):
        raise FlywheelError("Blotato media references must be publicly accessible HTTP(S) URLs")
    platform = str(row["platform"])
    text = f"{row['caption']}\n\n{row['cta']}: {row['destination_url']}"
    payload: dict[str, Any] = {
        "post": {
            "accountId": account_id,
            "content": {"text": text, "mediaUrls": media_urls, "platform": platform},
            "target": blotato_target(platform, args),
        }
    }
    if row["scheduled_at"]:
        payload["scheduledTime"] = row["scheduled_at"]
    elif args.use_next_free_slot:
        payload["useNextFreeSlot"] = True
    return payload


def command_blotato_payload(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    with connect(db_path) as connection:
        row = get_content(connection, args.content_id)
        account_id = args.account_id or platform_config(config, row["platform"]).get("account_id")
        if not account_id:
            raise FlywheelError("A Blotato account id is required")
        emit(build_blotato_payload(row, str(account_id), args))


def command_blotato_send(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    if not args.execute:
        raise FlywheelError("External publishing is disabled without --execute")
    api_key = os.environ.get("BLOTATO_API_KEY")
    if not api_key:
        raise FlywheelError("BLOTATO_API_KEY is not set")
    base_url = os.environ.get("BLOTATO_BASE_URL", "https://backend.blotato.com/v2").rstrip("/")
    with connect(db_path) as connection:
        row = get_content(connection, args.content_id)
        if row["approved_by"] != args.approved_by.strip():
            raise FlywheelError("--approved-by must match the recorded content approval")
        pconfig = platform_config(config, row["platform"])
        if pconfig.get("publishing_mode", "review_required") == "draft_only":
            raise FlywheelError("Platform publishing mode is draft_only")
        account_id = args.account_id or pconfig.get("account_id")
        if not account_id:
            raise FlywheelError("A Blotato account id is required")
        payload = build_blotato_payload(row, str(account_id), args)
        payload_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        request = urllib.request.Request(
            f"{base_url}/posts",
            data=payload_bytes,
            headers={"blotato-api-key": api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
            raise FlywheelError(f"Blotato returned HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise FlywheelError(f"Blotato request failed: {exc.reason}") from exc
        submission_id = str(result.get("postSubmissionId") or "") if isinstance(result, dict) else ""
        if not submission_id:
            raise FlywheelError("Blotato response did not include postSubmissionId; publication state is ambiguous")
        connection.execute(
            """INSERT INTO publications(content_id,platform,external_post_id,external_url,integration_id,payload_hash,state,published_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (args.content_id, row["platform"], submission_id, None, account_id, payload_hash, "submitted", utc_now()),
        )
        connection.execute("UPDATE content SET status='submitted' WHERE content_id=?", (args.content_id,))
    emit({"content_id": args.content_id, "platform": row["platform"], "post_submission_id": submission_id, "state": "submitted"})


def command_blotato_status(args: argparse.Namespace) -> None:
    _, _, db_path = load_campaign(args.workspace)
    api_key = os.environ.get("BLOTATO_API_KEY")
    if not api_key:
        raise FlywheelError("BLOTATO_API_KEY is not set")
    base_url = os.environ.get("BLOTATO_BASE_URL", "https://backend.blotato.com/v2").rstrip("/")
    with connect(db_path) as connection:
        publication = connection.execute(
            "SELECT * FROM publications WHERE external_post_id=? ORDER BY id DESC LIMIT 1",
            (args.post_submission_id,),
        ).fetchone()
        if publication is None:
            raise FlywheelError("Unknown Blotato post submission id")
        request = urllib.request.Request(
            f"{base_url}/posts/{urllib.parse.quote(args.post_submission_id)}",
            headers={"blotato-api-key": api_key},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
            raise FlywheelError(f"Blotato returned HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise FlywheelError(f"Blotato request failed: {exc.reason}") from exc
        state = str(result.get("status") or "unknown")
        public_url = result.get("publicUrl")
        connection.execute(
            "UPDATE publications SET state=?, external_url=? WHERE id=?",
            (state, public_url, publication["publication_id"]),
        )
        if state == "published":
            connection.execute("UPDATE content SET status='published' WHERE content_id=?", (publication["content_id"],))
        elif state == "failed":
            connection.execute("UPDATE content SET status='failed' WHERE content_id=?", (publication["content_id"],))
    emit({"post_submission_id": args.post_submission_id, "state": state, "public_url": public_url, "error": result.get("errorMessage")})


def command_record_publish(args: argparse.Namespace) -> None:
    _, _, db_path = load_campaign(args.workspace)
    with connect(db_path) as connection:
        row = get_content(connection, args.content_id)
        if row["status"] != "approved":
            raise FlywheelError("Only approved content can be recorded as published")
        connection.execute(
            """INSERT INTO publications(content_id,platform,external_post_id,external_url,integration_id,payload_hash,state,published_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (args.content_id, row["platform"], args.post_id, args.url, args.integration_id, args.payload_hash, "published", args.published_at or utc_now()),
        )
        connection.execute("UPDATE content SET status='published' WHERE content_id=?", (args.content_id,))
    emit({"content_id": args.content_id, "post_id": args.post_id, "state": "published"})


METRIC_FIELDS = (
    "impressions", "views", "average_watch_pct", "completion_rate", "shares", "saves", "comments",
    "profile_visits", "link_clicks", "signups", "trials", "purchases", "new_mrr", "one_time_revenue",
    "refunds", "content_cost",
)


def validate_metric(name: str, value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FlywheelError(f"Metric {name} must be numeric") from exc
    if number < 0:
        raise FlywheelError(f"Metric {name} cannot be negative")
    if name in {"average_watch_pct", "completion_rate"} and number > 1:
        raise FlywheelError(f"Metric {name} must be between 0 and 1")
    return number


def command_ingest_metrics(args: argparse.Namespace) -> None:
    _, _, db_path = load_campaign(args.workspace)
    source = load_json(Path(args.input).expanduser().resolve())
    snapshots = source.get("snapshots") if isinstance(source, dict) else source
    if not isinstance(snapshots, list) or not snapshots:
        raise FlywheelError("Input must contain a non-empty snapshots array")
    ingested = []
    with connect(db_path) as connection:
        for snapshot in snapshots:
            required_text(snapshot, ("content_id", "platform", "captured_at"))
            get_content(connection, str(snapshot["content_id"]))
            values = {name: validate_metric(name, snapshot.get(name, 0)) for name in METRIC_FIELDS}
            connection.execute(
                f"""INSERT OR REPLACE INTO metrics(content_id,platform,captured_at,{','.join(METRIC_FIELDS)})
                    VALUES({','.join('?' for _ in range(3 + len(METRIC_FIELDS)))})""",
                (
                    snapshot["content_id"],
                    str(snapshot["platform"]).lower(),
                    snapshot["captured_at"],
                    *[values[name] for name in METRIC_FIELDS],
                ),
            )
            ingested.append({"content_id": snapshot["content_id"], "platform": snapshot["platform"], "captured_at": snapshot["captured_at"]})
    emit({"ingested": ingested, "count": len(ingested)})


def latest_metric_rows(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT m.*, c.hook, c.hypothesis, c.experiment_cell, c.audience, c.problem
        FROM metrics m
        JOIN (
          SELECT content_id, platform, MAX(captured_at) AS captured_at
          FROM metrics GROUP BY content_id, platform
        ) latest
          ON m.content_id=latest.content_id AND m.platform=latest.platform AND m.captured_at=latest.captured_at
        JOIN content c ON c.content_id=m.content_id
        """
    ).fetchall()


def safe_rate(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def score_row(row: sqlite3.Row, config: dict[str, Any]) -> dict[str, Any]:
    experiment = config.get("experimentation", {})
    min_views = int(experiment.get("minimum_views_for_attention_decision", 1000))
    min_clicks = int(experiment.get("minimum_clicks_for_conversion_decision", 50))
    min_purchases = int(experiment.get("minimum_purchases_for_revenue_decision", 3))
    margin = float(config.get("goal", {}).get("gross_margin_rate", 1))
    impressions = float(row["impressions"])
    views = float(row["views"])
    clicks = float(row["link_clicks"])
    purchases = float(row["purchases"])
    revenue = float(row["new_mrr"]) + float(row["one_time_revenue"]) - float(row["refunds"])
    contribution = revenue * margin - float(row["content_cost"])
    contribution_per_1k = safe_rate(contribution * 1000, impressions)
    click_rate = safe_rate(clicks, views)
    signup_rate = safe_rate(float(row["signups"]), clicks)
    purchase_rate = safe_rate(purchases, float(row["trials"]) or float(row["signups"]))
    share_rate = safe_rate(float(row["shares"]), views)
    save_rate = safe_rate(float(row["saves"]), views)
    if purchases >= min_purchases:
        depth = "revenue"
        score = contribution_per_1k
        decision = "eligible_for_revenue_decision"
    elif clicks >= min_clicks:
        depth = "conversion"
        score = (signup_rate * 70 + purchase_rate * 30) * 100
        decision = "eligible_for_conversion_decision"
    elif views >= min_views:
        depth = "attention"
        score = (
            float(row["completion_rate"]) * 0.35
            + share_rate * 5
            + save_rate * 4
            + click_rate * 8
        ) * 100
        decision = "eligible_for_attention_decision"
    else:
        depth = "learning"
        score = 0
        decision = "insufficient_sample"
    return {
        "content_id": row["content_id"],
        "platform": row["platform"],
        "experiment_cell": row["experiment_cell"],
        "hypothesis": row["hypothesis"],
        "depth": depth,
        "decision_state": decision,
        "score": round(score, 4),
        "impressions": int(impressions),
        "views": int(views),
        "completion_rate": round(float(row["completion_rate"]), 4),
        "share_rate": round(share_rate, 4),
        "click_rate": round(click_rate, 4),
        "signup_rate": round(signup_rate, 4),
        "purchase_rate": round(purchase_rate, 4),
        "attributed_revenue": round(revenue, 2),
        "contribution_per_1k_impressions": round(contribution_per_1k, 2),
    }


def score_all(connection: sqlite3.Connection, config: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted((score_row(row, config) for row in latest_metric_rows(connection)), key=lambda item: item["score"], reverse=True)


def command_score(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    with connect(db_path) as connection:
        scores = score_all(connection, config)
    emit({"scores": scores, "count": len(scores)})


def command_report(args: argparse.Namespace) -> None:
    _, config, db_path = load_campaign(args.workspace)
    with connect(db_path) as connection:
        queue = {row["status"]: row["count"] for row in connection.execute("SELECT status,COUNT(*) AS count FROM content GROUP BY status")}
        scores = score_all(connection, config)
        latest = latest_metric_rows(connection)
        attributed_new_mrr = sum(float(row["new_mrr"]) for row in latest)
        revenue = sum(float(row["new_mrr"]) + float(row["one_time_revenue"]) - float(row["refunds"]) for row in latest)
        cost = sum(float(row["content_cost"]) for row in latest)
    current = float(config.get("goal", {}).get("current_mrr", 0)) + attributed_new_mrr
    goal = float(config.get("goal", {}).get("target_mrr", 0))
    emit(
        {
            "campaign_id": config.get("campaign_id"),
            "queue": queue,
            "economics": {
                "verified_base_mrr": config.get("goal", {}).get("current_mrr", 0),
                "attributed_new_mrr": round(attributed_new_mrr, 2),
                "operating_mrr": round(current, 2),
                "target_mrr": round(goal, 2),
                "target_gap": round(max(0, goal - current), 2),
                "attributed_revenue": round(revenue, 2),
                "content_cost": round(cost, 2),
            },
            "target_model": target_model(config),
            "top_evidence": scores[:5],
            "warnings": [] if scores else ["No metrics have been ingested; no winner can be selected."],
        }
    )


def command_schedule_spec(args: argparse.Namespace) -> None:
    root, _, _ = load_campaign(args.workspace)
    jobs = [
        {"id": "flywheel-health", "agent": "growth-orchestrator", "schedule": "*/15 * * * *", "action": f"Use $scale-revenue-flywheel to run health checks for {root}. Pause unsafe or ambiguous publishing and report only actionable failures."},
        {"id": "flywheel-research", "agent": "market-intelligence", "schedule": "17 */6 * * *", "action": f"Use $scale-revenue-flywheel to refresh cited market evidence and the experiment backlog for {root}. Do not copy competitor creative."},
        {"id": "flywheel-produce", "agent": "creative-producer", "schedule": "37 */2 * * *", "action": f"Use $scale-revenue-flywheel to fill approved experiment capacity for {root}. Generate and validate drafts only; do not publish."},
        {"id": "flywheel-publish", "agent": "publisher", "schedule": "7,22,37,52 * * * *", "action": f"Use $scale-revenue-flywheel to process due approved content for {root} within platform consent, audit, approval, and daily-cap rules."},
        {"id": "flywheel-metrics", "agent": "growth-analyst", "schedule": "41 */4 * * *", "action": f"Use $scale-revenue-flywheel to ingest and reconcile platform, product, and revenue metrics for {root}. Preserve attribution confidence."},
        {"id": "flywheel-optimize", "agent": "growth-orchestrator", "schedule": "23 22 * * *", "action": f"Use $scale-revenue-flywheel to score evidence and reallocate the experiment portfolio for {root}. Optimize the deepest credible funnel metric."},
        {"id": "flywheel-review", "agent": "revenue-analyst", "schedule": "31 16 * * 0", "action": f"Use $scale-revenue-flywheel to create the weekly economics, cohort, strategy, and risk report for {root}. Never claim unverified revenue."},
    ]
    for job in jobs:
        job["openclaw_command"] = [
            "openclaw", "cron", "create", job["schedule"], job["action"],
            "--name", job["id"], "--tz", args.timezone, "--session", "isolated", "--agent", job["agent"],
        ]
    emit({
        "timezone": args.timezone,
        "jobs": jobs,
        "note": "Create the named OpenClaw agents before running these commands, or remove --agent to use the configured default.",
    })


def add_postiz_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--integration-id", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--privacy-level", default="SELF_ONLY")
    parser.add_argument("--branded-content", action="store_true")
    parser.add_argument("--brand-organic", action="store_true")


def add_blotato_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--account-id", default="")
    parser.add_argument("--page-id", default="")
    parser.add_argument("--board-id", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--privacy-level", default="SELF_ONLY", choices=["SELF_ONLY", "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR"])
    parser.add_argument("--youtube-privacy", default="private", choices=["private", "public", "unlisted"])
    parser.add_argument("--media-type", default="reel", choices=["reel", "story"])
    parser.add_argument("--disabled-comments", action="store_true")
    parser.add_argument("--disabled-duet", action="store_true")
    parser.add_argument("--disabled-stitch", action="store_true")
    parser.add_argument("--branded-content", action="store_true")
    parser.add_argument("--your-brand", action="store_true")
    parser.add_argument("--not-ai-generated", action="store_true")
    parser.add_argument("--is-draft", action="store_true")
    parser.add_argument("--notify-subscribers", action="store_true")
    parser.add_argument("--use-next-free-slot", action="store_true")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Operate a governed content-to-revenue flywheel")
    sub = root.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize a campaign workspace")
    init.add_argument("--workspace", required=True)
    init.add_argument("--business", required=True)
    init.add_argument("--offer", required=True)
    init.add_argument("--landing-url", required=True)
    init.add_argument("--target-mrr", type=float, default=5000)
    init.add_argument("--current-mrr", type=float, default=0)
    init.add_argument("--arpu", type=float, default=49)
    init.add_argument("--churn", type=float, default=0.05)
    init.add_argument("--gross-margin", type=float, default=0.8)
    init.add_argument("--target-days", type=int, default=90)
    init.add_argument("--timezone", default="America/Los_Angeles")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=command_init)

    health = sub.add_parser("health", help="Check configuration and credential presence")
    health.add_argument("--workspace", required=True)
    health.set_defaults(func=command_health)

    model = sub.add_parser("model-target", help="Model the customer requirement for the MRR target")
    model.add_argument("--workspace", required=True)
    model.set_defaults(func=command_model_target)

    enqueue = sub.add_parser("enqueue", help="Validate and enqueue a structured content batch")
    enqueue.add_argument("--workspace", required=True)
    enqueue.add_argument("--input", required=True)
    enqueue.set_defaults(func=command_enqueue)

    approve = sub.add_parser("approve", help="Record human or policy-owner approval")
    approve.add_argument("--workspace", required=True)
    approve.add_argument("--content-id", required=True)
    approve.add_argument("--approved-by", required=True)
    approve.set_defaults(func=command_approve)

    queue = sub.add_parser("queue", help="List campaign content")
    queue.add_argument("--workspace", required=True)
    queue.add_argument("--status", default="")
    queue.add_argument("--platform", default="")
    queue.add_argument("--limit", type=int, default=50)
    queue.set_defaults(func=command_queue)

    payload = sub.add_parser("postiz-payload", help="Preview the exact Postiz request")
    add_postiz_arguments(payload)
    payload.set_defaults(func=command_postiz_payload)

    send = sub.add_parser("postiz-send", help="Publish approved content through Postiz")
    add_postiz_arguments(send)
    send.add_argument("--approved-by", required=True)
    send.add_argument("--execute", action="store_true")
    send.set_defaults(func=command_postiz_send)

    blotato_payload = sub.add_parser("blotato-payload", help="Preview the exact Blotato request")
    add_blotato_arguments(blotato_payload)
    blotato_payload.set_defaults(func=command_blotato_payload)

    blotato_send = sub.add_parser("blotato-send", help="Publish approved content through Blotato")
    add_blotato_arguments(blotato_send)
    blotato_send.add_argument("--approved-by", required=True)
    blotato_send.add_argument("--execute", action="store_true")
    blotato_send.set_defaults(func=command_blotato_send)

    blotato_status = sub.add_parser("blotato-status", help="Reconcile an asynchronous Blotato publication")
    blotato_status.add_argument("--workspace", required=True)
    blotato_status.add_argument("--post-submission-id", required=True)
    blotato_status.set_defaults(func=command_blotato_status)

    record = sub.add_parser("record-publish", help="Record a publication made by another approved adapter")
    record.add_argument("--workspace", required=True)
    record.add_argument("--content-id", required=True)
    record.add_argument("--post-id", required=True)
    record.add_argument("--url", default="")
    record.add_argument("--integration-id", default="")
    record.add_argument("--payload-hash", default="")
    record.add_argument("--published-at", default="")
    record.set_defaults(func=command_record_publish)

    ingest = sub.add_parser("ingest-metrics", help="Ingest cumulative platform and revenue snapshots")
    ingest.add_argument("--workspace", required=True)
    ingest.add_argument("--input", required=True)
    ingest.set_defaults(func=command_ingest_metrics)

    score = sub.add_parser("score", help="Score content at the deepest credible funnel stage")
    score.add_argument("--workspace", required=True)
    score.set_defaults(func=command_score)

    report = sub.add_parser("report", help="Produce an operating and economics report")
    report.add_argument("--workspace", required=True)
    report.set_defaults(func=command_report)

    schedule = sub.add_parser("schedule-spec", help="Generate logical OpenClaw scheduler jobs")
    schedule.add_argument("--workspace", required=True)
    schedule.add_argument("--timezone", default="America/Los_Angeles")
    schedule.set_defaults(func=command_schedule_spec)

    return root


def main() -> int:
    args = parser().parse_args()
    try:
        args.func(args)
        return 0
    except FlywheelError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
