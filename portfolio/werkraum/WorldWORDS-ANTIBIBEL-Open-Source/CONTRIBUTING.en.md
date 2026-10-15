# Contributing

## Fastest path

1. Open an issue using the **New term** template.
2. Enter the raw form exactly. Do not correct it.
3. Separate submitter, possible author and uncertainty.
4. Add date, context, exact wording and a publishable source.
5. Explain the term in German, English or Spanish. More languages are welcome.
6. State explicitly what the term does not mean.
7. Submit a pull request containing a file under `data/proposals/`.

## Minimum fields

- `id`
- `raw_form`
- `submitted_by`
- `authorship_status`
- `first_seen`
- `exact_input`
- `source_ref`
- `definitions`
- `status: submitted`

## What happens next

Technical checks validate schema, IDs, source fields, date formats and accidental secrets. Provenance review may follow. Only Daniel can set an official-registry item to `accepted` and create the corresponding decision record.

## Corrections

Do not silently replace old provenance. Submit a new event with `event_type: correction` and point to the incorrect event.

## Translations

Translate explanations, boundaries and examples. Preserve the raw form. A new word form in another language is a separate proposal, not an ordinary translation.

## Rights

By contributing, you confirm that you may publish the material under the repository licenses. Do not submit complete third-party chats, books, articles or private messages without permission.
