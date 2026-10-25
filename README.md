---
license: cc-by-nc-sa-4.0
pretty_name: Real-IAD-MVN
tags:
  - image
  - industrial-anomaly-detection
  - multi-view
---

# Real-IAD-MVN

This release contains 20 category directories, 8,700 sample directories (ng: 3700, ok: 5000), and 104,339 image files. Counts refer to the files indexed in this release.

## Release organization

```text
Real-IAD-MVN/
├── README.md
├── ReadMe.txt
├── LICENSE.txt
├── .gitattributes
├── dataset_info.json
├── dataset.json
├── realiad_mvn_jsons.zip
├── metadata/
│   └── samples.jsonl
├── format/
├── paper_comparison.json
├── quality_report.json
├── packaging_report.json
├── SHA256SUMS
├── RELEASE_READY.json
├── verify_release.py
└── realiad_mvn_raw/
    ├── dc_power_connector.zip
    ├── fork_crimp_terminal.zip
    └── ... (one ZIP per category)
```

The archive-based release organization follows the [Real-IAD D³ repository](https://huggingface.co/datasets/Real-IAD/Real-IAD_D3/tree/main).

## Paper and dataset scope

The associated paper is [Real-IAD MVN: A Multi-View Normal Vector Dataset and Benchmark for High-Fidelity Industrial Anomaly Detection](https://arxiv.org/html/2605.07149v1). Section 3.3 describes 20 object categories, 8,450 samples (5,000 normal and 3,450 abnormal), five RGB images and five surface-normal maps per sample, with pixel-level masks where available for abnormal samples.

This release preserves all files scanned from the supplied source directories. Its counts are shown above and in `dataset_info.json`. `paper_comparison.json` compares the source directory counts against the paper's sample counts. Category-specific defect directory names are retained verbatim; their count is reported as a directory count.

## Data partitioning

This release does not introduce a train/validation/test partition or a `split` field. The cited paper version does not specify the partition ratios, sample assignments or random seed needed to reproduce an official partition. Each sample directory and all its views remain together in one record.

## Extraction and file paths

Extract each category ZIP into `realiad_mvn_raw/`. Each ZIP contains a directory named after its English category identifier. Within that directory, the original status, defect, sample, view directories and image filenames are retained. Images are copied without resizing, conversion or recompression.

Extract `realiad_mvn_jsons.zip` into the dataset root. It contains `realiad_mvn_jsons/<category>.json`, one index per category. `path` is relative to the extracted `realiad_mvn_raw/` directory. `source_path` records the path in the original dataset. Both use `/` separators.

`dataset.json` is the complete aggregate JSON, with dataset statistics in `dataset_info` and all sample records in `samples`. `metadata/samples.jsonl` contains one sample record per line. Category records in the aggregate JSON/JSONL also carry `category`. Images outside sample directories are retained in a separate `files_outside_sample_directories` array in `dataset.json` and in the category index.

## JSON index fields

These are the index fields used by this release:

| Field | Meaning |
| --- | --- |
| `category` | English category identifier used in this release |
| `source_directory_name` | Original category directory name |
| `samples` | Records grouped by original `S<number>` directory |
| `sample_id` | Unique identifier based on category, status, defect and sample directory |
| `sample_directory` | Sample directory relative to `realiad_mvn_raw/` |
| `sample_directory_name` | Original sample directory basename |
| `status_directory_name` | Original `ok` or `ng` directory name, when present |
| `defect_directory_name` | Original intervening defect directory, when present |
| `views` | Files grouped by observed `C<number>` directory |
| `view_directory_name` | Original view directory name |
| `files` | All image files in that group, including mask-named images |
| `path` | Released file path relative to `realiad_mvn_raw/` |
| `source_path` | Corresponding original relative file path |
| `bytes` | Byte length read when the image was packaged |
| `sha256` | SHA-256 of the exact original image bytes |
| `filename_group` | Literal filename match, included only when a rule matches |

Images outside a view or sample directory are retained in `files_outside_view_directories` or `files_outside_sample_directories`, respectively, when present. Directory identifiers are retained as recorded. Filename rules match `mask`, `RGBL05`/a separated `RGB` token, or a separated `PS` token; mask matching takes precedence. These matches are file-discovery aids. Every image is retained, including files without a match. Multiple matches are kept as separate file entries.

```python
import json
from pathlib import Path

root = Path("Real-IAD-MVN")
index = json.loads((root / "realiad_mvn_jsons/dc_power_connector.json").read_text(encoding="utf-8"))
sample = index["samples"][0]
file_path = root / "realiad_mvn_raw" / sample["views"][0]["files"][0]["path"]
print(file_path)
```

## Measured image properties

`format/format_measurements.json` summarizes measured headers and all decoded pixels of mask-named files. `format/image_headers.jsonl` records width, height, file format, Pillow mode/bands, and stored PNG/JPEG bit depth when read from the file. `format/mask_pixel_values.jsonl` records exact decoded mask pixel values; large value sets are saved as `.npy` files under `format/pixel_values/`.

Dimension comparisons report equality of image dimensions. They do not establish geometric alignment. No normal-vector decoding formula, camera orientation, coordinate axes, mask threshold or pixel-label interpretation is assigned by this packaging process.

`quality_report.json` records filename matches, view directory counts, duplicate filenames by group, dimension differences and file read failures. All source images are preserved. `paper_comparison.json` records factual count comparisons; image counts and sample-directory counts are distinct units.

## Integrity verification

`SHA256SUMS` contains SHA-256 checksums for the published files other than the checksum list itself. Each image also has its own digest in the JSON indexes. `RELEASE_READY.json` is written only after archives and JSON references pass structural verification.

After downloading or copying the release, run:

```bash
python3 verify_release.py --root /path/to/Real-IAD-MVN-hf
```

This checks every published-file checksum, category archive entries, their byte lengths, sample IDs, JSON coverage and the absence of introduced data partitions. No original server files are required.

## Categories

| Category | Sample directories | Image files |
| --- | ---: | ---: |
| dc_power_connector | 450 | 5498 |
| fork_crimp_terminal | 400 | 4657 |
| ethernet_connector | 400 | 4748 |
| fuse_holder | 400 | 4742 |
| common_mode_filter | 450 | 5477 |
| crimp_st_cable_mount_box | 450 | 5410 |
| connector_housing_female | 450 | 5487 |
| lego_pin_connector_plate | 450 | 5331 |
| knob_cap | 400 | 4643 |
| lattice_block_plug | 450 | 5164 |
| humidity_sensor | 450 | 5493 |
| ferrite_bead | 350 | 3999 |
| power_jack | 450 | 5348 |
| telephone_spring_switch | 500 | 6250 |
| miniature_lifting_motor | 350 | 3982 |
| purple_clay_pot | 450 | 5500 |
| headphone_jack_socket | 500 | 6243 |
| lego_propeller | 400 | 4736 |
| limit_switch | 450 | 5456 |
| audio_jack_socket | 500 | 6175 |

## License

The released dataset is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). See `LICENSE.txt` for the full license text.

## Upload

See `UPLOAD.md` for uploading the complete generated release directory to a Hugging Face dataset repository.
