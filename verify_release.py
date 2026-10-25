"""Verify a prepared Real-IAD-MVN release without original source data."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile


def sample_files(sample):
    for view in sample['views']:
        yield from view['files']
    yield from sample.get('files_outside_view_directories', [])


def document_files(document):
    for sample in document['samples']:
        yield from sample_files(sample)
    yield from document.get('files_outside_sample_directories', [])


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_partition_fields(value):
    if isinstance(value, dict):
        require('split' not in value and 'splits' not in value, 'Unexpected partition field')
        for item in value.values():
            no_partition_fields(item)
    elif isinstance(value, list):
        for item in value:
            no_partition_fields(item)


def safe_relative(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name, 'Unsafe relative path: '+name)
    require(name not in {'', '.'}, 'Empty file path')
    return path


def check_structure(root):
    root = Path(root).resolve(strict=True)
    info = json.loads((root / 'dataset_info.json').read_text(encoding='utf-8'))
    aggregate = json.loads((root / 'dataset.json').read_text(encoding='utf-8'))
    no_partition_fields(aggregate)
    require(info == aggregate['dataset_info'], 'Aggregate statistics disagree with dataset_info.json')
    categories = [c['category'] for c in info['categories']]
    require(len(categories) == len(set(categories)) == info['category_count'], 'Duplicate category identifiers')
    aggregate_samples = {s['sample_id']: s for s in aggregate['samples']}
    require(len(aggregate_samples) == len(aggregate['samples']) == info['sample_directory_count'], 'Duplicate or missing sample IDs')
    jsonl_count = 0
    jsonl_ids = set()
    with (root / 'metadata' / 'samples.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            sample_id = row['sample_id']
            require(sample_id not in jsonl_ids and aggregate_samples.get(sample_id) == row, 'JSONL disagrees with aggregate sample: '+sample_id)
            jsonl_ids.add(sample_id)
            jsonl_count += 1
    require(jsonl_ids == set(aggregate_samples), 'JSONL sample coverage differs')
    outside = {f['path']: f for f in aggregate.get('files_outside_sample_directories', [])}
    require(len(outside) == len(aggregate.get('files_outside_sample_directories', [])), 'Duplicate files outside sample directories')
    all_paths = set()
    all_source_paths = set()
    seen_samples = set()
    observed_statuses = Counter()
    extensions = Counter()
    with zipfile.ZipFile(root / 'realiad_mvn_jsons.zip') as indexes:
        expected_names = {'realiad_mvn_jsons/'+c+'.json' for c in categories}
        require(len(indexes.namelist()) == len(expected_names) and set(indexes.namelist()) == expected_names, 'Category JSON coverage differs')
        for category in categories:
            document = json.loads(indexes.read('realiad_mvn_jsons/'+category+'.json'))
            no_partition_fields(document)
            require(document['category'] == category, 'Incorrect category JSON identifier')
            class_info = next(c for c in info['categories'] if c['category'] == category)
            require(len(document['samples']) == class_info['sample_directory_count'], 'Category sample count differs')
            for sample in document['samples']:
                sample_id = sample['sample_id']
                require(sample_id not in seen_samples, 'Sample appears in multiple category indexes')
                require(aggregate_samples.get(sample_id) == {'category': category, **sample}, 'Category sample differs from aggregate')
                seen_samples.add(sample_id)
                observed_statuses[sample.get('status_directory_name', '')] += 1
            for file in document.get('files_outside_sample_directories', []):
                require(outside.pop(file['path'], None) == {'category': category, **file}, 'Outside-sample image differs from aggregate')
            files = list(document_files(document))
            require(len(files) == class_info['image_file_count'], 'Category image count differs')
            expected_entries = {f['path']: f for f in files}
            require(len(expected_entries) == len(files), 'Duplicate category file path')
            with zipfile.ZipFile(root / 'realiad_mvn_raw' / (category+'.zip')) as archive:
                names = archive.namelist()
                require(len(names) == len(expected_entries) and set(names) == set(expected_entries), 'Image archive coverage differs: '+category)
                for entry in archive.infolist():
                    record = expected_entries[entry.filename]
                    path = safe_relative(entry.filename)
                    safe_relative(record['source_path'])
                    require(path.parts[0] == category, 'Image path has the wrong category')
                    require(entry.filename not in all_paths and record['source_path'] not in all_source_paths, 'Image is indexed multiple times')
                    require(entry.file_size == record['bytes'], 'Image byte length differs: '+entry.filename)
                    require(re.fullmatch(r'[0-9a-f]{64}', record['sha256']) is not None, 'Missing image SHA-256')
                    all_paths.add(entry.filename)
                    all_source_paths.add(record['source_path'])
                    extensions[path.suffix.lower()] += 1
    require(seen_samples == set(aggregate_samples) and not outside, 'Category indexes do not cover all aggregate records')
    require(len(all_paths) == info['image_file_count'], 'Total image count differs')
    require(dict(observed_statuses) == info['sample_directory_counts_by_status'], 'Status directory counts differ')
    require(dict(extensions) == info['image_file_extensions'], 'Image extension counts differ')
    return {'category_count': len(categories), 'sample_record_count': len(seen_samples),
            'image_file_count': len(all_paths), 'jsonl_record_count': jsonl_count,
            'introduced_partition_fields': 0}


def check_checksums(root):
    root = Path(root).resolve(strict=True)
    require((root / 'RELEASE_READY.json').is_file(), 'Release completion marker is missing')
    count = 0
    seen = set()
    with (root / 'SHA256SUMS').open(encoding='utf-8') as stream:
        for line in stream:
            digest, name = line.rstrip('\n').split('  ', 1)
            path = safe_relative(name)
            require(re.fullmatch(r'[0-9a-f]{64}', digest) is not None and name not in seen, 'Invalid checksum entry')
            target = root.joinpath(*path.parts)
            require(target.is_file() and not target.is_symlink() and root in target.resolve().parents, 'Missing or unsafe published file: '+name)
            actual = hashlib.sha256()
            with target.open('rb') as content:
                for chunk in iter(lambda: content.read(1024*1024), b''):
                    actual.update(chunk)
            require(actual.hexdigest() == digest, 'Checksum mismatch: '+name)
            seen.add(name)
            count += 1
            print('Checksum OK: '+name, flush=True)
    expected = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'SHA256SUMS' and not any(part.startswith('.') and part != '.gitattributes' for part in p.relative_to(root).parts)}
    require(expected <= seen, 'Files missing from checksum list: '+', '.join(sorted(expected-seen)))
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    args = parser.parse_args()
    count = check_checksums(args.root)
    report = check_structure(args.root)
    print(json.dumps({'status':'passed','published_file_checksums_checked':count, **report}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
