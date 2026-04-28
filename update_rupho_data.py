import argparse
import json
import os
import re
from pathlib import Path

PDF_PATTERN = re.compile(r'^(?P<base>.+?)(?:_S)?_EN_2\.pdf$', flags=re.IGNORECASE)


def natural_sort_key(value: str):
    parts = re.split(r'(\d+)', value)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def parse_pdf_filename(filename: str):
    normalized = filename.replace('\\', '/')
    match = PDF_PATTERN.match(normalized)
    if not match:
        return None
    base = match.group('base')
    is_solution = normalized.lower().endswith('_s_en_2.pdf')
    key = f'{base}_EN_2'
    label = base
    return key, label, is_solution


def gather_section_files(root_path: Path, section: str):
    section_path = root_path / section
    if not section_path.is_dir():
        return {}

    years = sorted(
        [entry.name for entry in section_path.iterdir() if entry.is_dir() and entry.name.isdigit()],
        key=lambda x: int(x),
        reverse=False,
    )

    section_data = {}
    for year in years:
        year_path = section_path / year
        items = {}
        for entry in sorted(year_path.iterdir()):
            if not entry.is_file():
                continue
            result = parse_pdf_filename(entry.name)
            if result is None:
                continue
            key, label, is_solution = result
            item = items.setdefault(
                key,
                {
                    'key': key,
                    'label': label,
                    'problem': None,
                    'solution': None,
                },
            )
            relative_path = f'{section}/{year}/{entry.name}'
            if is_solution:
                item['solution'] = relative_path
            else:
                item['problem'] = relative_path

        if items:
            section_data[year] = sorted(items.values(), key=lambda item: natural_sort_key(item['key']))

    return section_data


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f'Wrote {path}')


def write_js_bundle(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        f.write('window.ruphoData = ')
        json.dump(data, f, indent=2)
        f.write(';\n')
    print(f'Wrote {path}')


def main():
    parser = argparse.ArgumentParser(description='Generate rupho site data from rupho-x, rupho-y, and rupho-w folders.')
    parser.add_argument('--root', default='.', help='Repository root path containing rupho-x, rupho-y, rupho-w.')
    parser.add_argument('--sections', default='rupho-x,rupho-y,rupho-w', help='Comma-separated section directories to process.')
    parser.add_argument('--json-out', default='assets/rupho-data.json', help='Output JSON file path.')
    parser.add_argument('--js-out', default='assets/rupho-data.js', help='Output JS bundle path.')
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    sections = [section.strip() for section in args.sections.split(',') if section.strip()]
    data = {}

    for section in sections:
        section_data = gather_section_files(root_path, section)
        data[section] = section_data
        print(f'  {section}: {sum(len(year_items) for year_items in section_data.values())} items across {len(section_data)} years')

    write_json(root_path / args.json_out, data)
    write_js_bundle(root_path / args.js_out, data)


if __name__ == '__main__':
    main()
