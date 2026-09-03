#!/usr/bin/env python3
"""
kirim_info_lomba.py — Kirim info lomba BARU (hasil cari_lomba.py) ke WhatsApp
lewat WhatsApp gateway lokal (base URL & login diatur di wa_config.yaml).

Jalan:
    python kirim_info_lomba.py --dry-run     # preview dulu, TIDAK kirim apa pun
    python kirim_info_lomba.py               # kirim beneran ke recipients di wa_config.yaml

Dedup otomatis: lomba yang sudah pernah dikirim (tercatat di wa_sent_history.json,
key-nya link masing-masing lomba) tidak akan dikirim ulang di run berikutnya.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml
from requests.auth import HTTPBasicAuth

import cari_lomba as cl


def load_wa_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_history(path: Path) -> dict:
    if not path.exists():
        return {"sent": {}}
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {"sent": {}}
    data.setdefault("sent", {})
    return data


def save_history(path: Path, history: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def item_key(item: "cl.Lomba") -> str:
    # Link paling stabil sebagai kunci unik dedup; fallback ke judul kalau link kosong.
    if item.link:
        return item.link.strip().lower()
    return "title:" + item.title.strip().lower()


def format_item(item: "cl.Lomba") -> str:
    deadline_s = item.deadline.strftime("%d %b %Y") if item.deadline else "tidak diketahui"
    start_s = item.start_date.strftime("%d %b %Y") if item.start_date else "tidak diketahui"
    return (
        f"*[{item.category}] {item.title}*\n"
        f"Deadline: {deadline_s}\n"
        f"Pelaksanaan: {start_s}\n"
        f"Sumber: {item.source}\n"
        f"Link: {item.link}"
    )


def chunk_list(items: list, size: int) -> list:
    size = max(1, size)
    return [items[i:i + size] for i in range(0, len(items), size)]


def build_messages(new_items: list, max_per_message: int) -> list:
    chunks = chunk_list(new_items, max_per_message)
    messages = []
    for i, chunk in enumerate(chunks, 1):
        body = "\n\n".join(format_item(it) for it in chunk)
        header = f"\U0001F4CB *Info Lomba Baru* (bagian {i}/{len(chunks)}, {len(chunk)} lomba)\n\n"
        messages.append(header + body)
    return messages, chunks


class WaGatewayError(Exception):
    pass


def _gw_headers(gw: dict) -> dict:
    headers = {}
    if gw.get("device_id"):
        headers["X-Device-Id"] = gw["device_id"]
    return headers


def send_text(gw: dict, phone: str, message: str) -> None:
    url = gw["base_url"].rstrip("/") + "/send/message"
    try:
        resp = requests.post(
            url,
            auth=HTTPBasicAuth(gw["username"], gw["password"]),
            json={"phone": phone, "message": message},
            headers=_gw_headers(gw),
            timeout=20,
        )
    except requests.exceptions.ConnectionError as e:
        raise WaGatewayError(
            f"Gagal konek ke WhatsApp gateway di {gw['base_url']} — pastikan servernya sudah jalan."
        ) from e
    if resp.status_code >= 400:
        raise WaGatewayError(f"Gateway balas error {resp.status_code} untuk {phone}: {resp.text[:300]}")


def send_link(gw: dict, phone: str, link: str, caption: str) -> None:
    url = gw["base_url"].rstrip("/") + "/send/link"
    try:
        resp = requests.post(
            url,
            auth=HTTPBasicAuth(gw["username"], gw["password"]),
            json={"phone": phone, "link": link, "caption": caption},
            headers=_gw_headers(gw),
            timeout=20,
        )
    except requests.exceptions.ConnectionError as e:
        raise WaGatewayError(
            f"Gagal konek ke WhatsApp gateway di {gw['base_url']} — pastikan servernya sudah jalan."
        ) from e
    if resp.status_code >= 400:
        raise WaGatewayError(f"Gateway balas error {resp.status_code} untuk {phone}: {resp.text[:300]}")


def all_recipients(wa_config: dict) -> list:
    recipients = list(wa_config.get("recipients", {}).get("personal", []) or [])
    recipients += list(wa_config.get("recipients", {}).get("groups", []) or [])
    return [r for r in recipients if r and r.strip()]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Kirim info lomba baru ke WhatsApp")
    parser.add_argument("--wa-config", default="wa_config.yaml", help="Path ke wa_config.yaml")
    parser.add_argument("--lomba-config", default="config.yaml", help="Path ke config.yaml (cari_lomba)")
    parser.add_argument("--days", type=int, default=None, help="Hanya lomba dengan deadline dalam N hari ke depan")
    parser.add_argument("--dry-run", action="store_true",
                         help="Cuma preview di terminal, TIDAK mengirim apa pun & TIDAK update history")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    wa_config_path = Path(args.wa_config)
    if not wa_config_path.is_absolute():
        wa_config_path = base_dir / wa_config_path
    lomba_config_path = Path(args.lomba_config)
    if not lomba_config_path.is_absolute():
        lomba_config_path = base_dir / lomba_config_path

    wa_config = load_wa_config(wa_config_path)
    lomba_config = cl.load_config(lomba_config_path)

    history_path = base_dir / wa_config.get("history_file", "wa_sent_history.json")
    history = load_history(history_path)
    sent_keys = set(history["sent"].keys())

    if not args.dry_run and not cl.cek_sinyal():
        print("[!] Internet kamu kelihatannya belum konek. Batalkan dulu.", file=sys.stderr)
        sys.exit(1)

    print("[*] Mengumpulkan info lomba...")
    items = cl.collect(lomba_config, [])
    items = cl.filter_by_days(items, args.days, include_closed=False)
    items = cl.sort_items(items)

    new_items = [it for it in items if item_key(it) not in sent_keys]

    if not new_items:
        print("[*] Tidak ada lomba baru yang belum pernah dikirim. Selesai.")
        return

    print(f"[*] Ada {len(new_items)} lomba baru (dari total {len(items)} yang relevan).")

    recipients = all_recipients(wa_config)
    if not recipients:
        print(
            "[!] Belum ada nomor/grup tujuan di wa_config.yaml. "
            "Isi dulu recipients.personal / recipients.groups.",
            file=sys.stderr,
        )
        sys.exit(1)

    max_per_msg = wa_config.get("max_items_per_message", 10)
    send_mode = wa_config.get("send_mode", "single_text")

    if args.dry_run:
        print("\n[DRY RUN] Tidak ada pesan yang benar-benar dikirim.\n")
        if send_mode == "per_item_link":
            for it in new_items:
                print(f"--- akan dikirim ke {len(recipients)} tujuan ---")
                print(format_item(it))
                print()
        else:
            messages, _ = build_messages(new_items, max_per_msg)
            for msg in messages:
                print(f"--- akan dikirim ke {len(recipients)} tujuan ---")
                print(msg)
                print()
        return

    gw = wa_config["gateway"]
    sent_ok_keys = []
    had_error = False

    if send_mode == "per_item_link":
        for it in new_items:
            caption = format_item(it)
            ok = True
            for phone in recipients:
                try:
                    send_link(gw, phone, it.link, caption)
                except WaGatewayError as e:
                    print(f"[!] Gagal kirim ke {phone}: {e}", file=sys.stderr)
                    had_error = True
                    ok = False
            if ok:
                sent_ok_keys.append(item_key(it))
    else:
        messages, chunks = build_messages(new_items, max_per_msg)
        for msg, chunk in zip(messages, chunks):
            ok = True
            for phone in recipients:
                try:
                    send_text(gw, phone, msg)
                except WaGatewayError as e:
                    print(f"[!] Gagal kirim ke {phone}: {e}", file=sys.stderr)
                    had_error = True
                    ok = False
            if ok:
                sent_ok_keys.extend(item_key(it) for it in chunk)

    now = datetime.now().isoformat(timespec="seconds")
    for k in sent_ok_keys:
        history["sent"][k] = now
    save_history(history_path, history)

    print(f"[*] Selesai. {len(sent_ok_keys)} lomba tercatat sudah dikirim & dicatat di history.")
    if had_error:
        print(
            "[!] Ada sebagian pengiriman yang gagal (lihat pesan error di atas). "
            "Lomba yang gagal TIDAK dicatat sebagai sudah terkirim, jadi akan dicoba "
            "lagi di run berikutnya.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
