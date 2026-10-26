# HydroScholar AI Case-Study Artifact Archive

<p align="center">
  <img src="assets/usgs-logo.png" alt="U.S. Geological Survey logo" width="210">
  &nbsp;&nbsp;&nbsp;
  <img src="assets/tulane-logo.png" alt="Tulane University logo" width="180">
</p>

**Hydroinformatics Lab at Tulane University**

The USGS identifier is included with permission using approved artwork. See the [USGS Visual Identity System guidance](https://www.usgs.gov/information-policies-and-instructions/usgs-visual-identity-system).

This repository contains the five archived case-study evidence packages associated with the HydroScholar AI directed-graph workflow manuscript. It is an artifact archive, not the HydroScholar AI software repository.

## Scope

The archive is intended to make the retained experiment record inspectable. It contains, where available:

- experiment plans, prompts, designs, and configuration records (`experiment_plan.json`, `manifest.json`, `requirements.txt`);
- timestamped provenance, execution logs, gate records, and recovery notes (`provenance.jsonl`, `global_audit_trace.jsonl`);
- generated Python and shell task scripts produced during workflow execution (`.py`, `.sh`, with external API credentials redacted as `<REDACTED_CDS_API_KEY>`);
- raw and processed tabular data products, serialized model architectures and weights (`.json`, `.weights.h5`, `.pkl`), and sub-25 MiB NetCDF spatial grids (`.nc`);
- generated figures, plots, metrics, reports, and manuscript-ready outputs;
- references to excluded raw binary files exceeding 25 MiB and LaTeX build logs through `MANIFEST.csv`.

The HydroScholar AI application source code, virtual environments, compiled binaries, credentials, caches, and raw scientific-binary datasets exceeding 25 MiB are not included.

## Organization

Each folder under `experiments/` corresponds to one of the five case studies in the manuscript. A non-sensitive timestamped source-archive identifier is recorded in `EXPERIMENT_INDEX.csv` so that each package can be reconciled with its originating provenance record without exposing local filesystem paths.

- `experiments/<case-id>/` — case-study artifacts and a folder-level `ARCHIVE_README.md`;
- `CASE_EVIDENCE_MATRIX.md` — claim-focused map from each case to the retained plan, provenance, selected artifacts, observed behavior, and limitations;
- `EXPERIMENT_INDEX.csv` — one row per manuscript case study, its non-sensitive source-archive identifier, and package counts;
- `MANIFEST.csv` — file-level inclusion/exclusion status and checksums for included files;
- `BUILD_METADATA.json` — construction metadata for this artifact package.

## Important interpretation note

These folders document workflow executions and their associated evidence. They should not automatically be interpreted as complete, independently validated hydrologic studies. Evidence completeness varies by case. The archive supports a case-specific audit of workflow plans, retained provenance, generated scripts, selected outputs, observed behavior, and limitations; it does not establish uniform end-to-end completion, independent replication, aggregate performance, comparative effectiveness, or hydrologic validity.

## Included case studies

- CS-I — Willamette River precipitation–streamflow correlation;
- CS-II — St. John River Random Forest streamflow prediction;
- CS-III — Lake Oroville satellite surface-water monitoring;
- CS-IV — Onion Creek LSTM rainfall–runoff modelling;
- CS-V — ERA5 statistical downscaling over the Columbia River Basin.

No other experiment folders from the larger local archive are included.

## Software and data boundary

This repository intentionally does not distribute the HydroScholar AI application source code. The artifact folders preserve the case-specific generated task scripts, provenance logs, datasets, model artifacts, and sub-25 MiB spatial grids for inspection of experiment evidence. Raw binary datasets exceeding 25 MiB (specifically the 15 raw Sentinel-2 GeoTIFF band files `data/satellite/*.tif` in CS-III at 219–280 MiB each, and the three raw hourly ERA5 NetCDF archives `data/era5_2021_hourly.nc`, `data/era5_2022_hourly.nc`, and `data/era5_2023_hourly.nc` in CS-V at 26.9–28.5 MiB each) are excluded due to GitHub file-size limits and are recorded in `MANIFEST.csv`.

## Integrity and versioning

`MANIFEST.csv` records SHA-256 hashes of included files. The repository uses `.gitattributes` to keep text files at LF line endings, so the manifest hashes are stable for a release checked out from Git. Before making a release, regenerate and validate the manifest against the exact release contents.

The case-evidence matrix becomes citable when this repository is tagged with a release version and archived in Zenodo or an equivalent service. Until then, it is release-supporting documentation rather than a persistent archival citation.

## Repository and archival identifiers

- GitHub repository: <https://github.com/uihilab/hydroscholar-ai-case-study-artifacts>
- Persistent archival identifier (Zenodo or equivalent): not yet assigned
- Manuscript data/code availability statement: update with the release tag and persistent archival identifier before submission.

## Branding

The repository includes the approved USGS and supplied Tulane University logo files and uses the name **Hydroinformatics Lab at Tulane University**. Do not replace or modify the institutional marks without approval.

## Citation

Please cite the associated manuscript and, once deposited, the persistent archival release. A release-specific citation file should be added after the version, authorship, and archival identifier are finalized.

## License and access review

No license is asserted by this preparation step. Before public release, the authors should confirm data-redistribution permissions, third-party terms, institutional branding approval, personally identifying information, API keys or credentials, and any restrictions attached to downloaded data.
