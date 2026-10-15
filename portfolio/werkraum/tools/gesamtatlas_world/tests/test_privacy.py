from app import redact_secrets


def main() -> None:
    source = (
        "Mail: person@example.org\n"
        "Telefon: +49 176 12345678\n"
        "IBAN: DE89 3704 0044 0532 0130 00\n"
        "Token: sk-abcdefghijklmnopqrstuvwxyz123456\n"
        "Unkritisch: Flextrawurst und Atlas bleiben lesbar."
    )
    redacted, count = redact_secrets(source)
    assert count >= 4, (count, redacted)
    assert "person@example.org" not in redacted
    assert "+49 176 12345678" not in redacted
    assert "DE89 3704 0044 0532 0130 00" not in redacted
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in redacted
    assert "Flextrawurst und Atlas bleiben lesbar" in redacted
    print({"ok": True, "redactions": count, "result": redacted})


if __name__ == "__main__":
    main()
