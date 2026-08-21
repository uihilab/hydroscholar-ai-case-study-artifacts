# HydroScholar AI Case-Study Artifact Archive

<p align="center">
  <img src="assets/tulane-logo.png" alt="Tulane University logo" width="180">
</p>

**the Hydroinformatics Lab at Tulane University**

The USGS identifier is not bundled until written permission and approved artwork are confirmed. See the [USGS Visual Identity System guidance](https://www.usgs.gov/information-policies-and-instructions/usgs-visual-identity-system).

This repository contains the five archived case-study artifacts associated with the HydroScholar AI manuscript. It is an artifact repository, not the HydroScholar AI software repository.

## Scope

The archive is intended to make the experiment record inspectable and citable. It contains, where available:

- experiment plans, prompts, designs, and configuration records;
- timestamped provenance, execution logs, gate records, and recovery notes;
- raw or processed tabular data products that are small enough for repository distribution;
- generated figures, plots, metrics, reports, and manuscript-ready outputs;
- experiment-local script references through the manifest; executable/source files are not copied in this artifact-only preparation.

The HydroScholar AI application source code, virtual environments, compiled binaries, credentials, caches, and large scientific-binary datasets are not included.

## Organization

Each folder under `experiments/` corresponds to one of the five case studies in the manuscript. The original timestamped archive path is recorded in `EXPERIMENT_INDEX.csv` so that each package can be reconciled with its originating provenance record.

- `experiments/<timestamped-experiment>/` — selected case-study artifacts and a folder-level `ARCHIVE_README.md`;
- `EXPERIMENT_INDEX.csv` — one row per manuscript case study and its source archive;
- `MANIFEST.csv` — file-level inclusion/exclusion status and checksums for included files;
- `BUILD_METADATA.json` — construction metadata for this artifact package.

## Important interpretation note

These folders document workflow executions and their associated evidence. They should not automatically be interpreted as complete, independently validated hydrologic studies. Case-study claims in the manuscript must remain bounded by the data, provenance, metrics, and limitations preserved in each folder.

## Included case studies

- CS-I — Willamette River precipitation–streamflow correlation;
- CS-II — St. John River Random Forest streamflow prediction;
- CS-III — Lake Oroville satellite surface-water monitoring;
- CS-IV — Onion Creek LSTM rainfall–runoff modelling;
- CS-V — ERA5 statistical downscaling over the Columbia River Basin.

No other experiment folders from the larger local archive are included.

## Willamette River case study (CS-I)

The Willamette River precipitation–streamflow case study is retained as a completed workflow-execution demonstration. Its archive contains the workflow plan, provenance, generated scripts, data products, plots, and correlation metrics. The manuscript describes its hydrologic analysis as exploratory and does not present it as a full independent hydrologic evaluation.

## Software and data boundary

This repository intentionally does not distribute the HydroScholar AI application source code. The artifact folders are preserved for inspection of experiment evidence, not as a software release. Large datasets and scientific-binary files excluded by the build are recorded in `MANIFEST.csv`; they should be deposited in an appropriate data repository if public redistribution is required.

## Repository and archival identifiers

- GitHub repository: **[INSERT FINAL GITHUB URL]**
- Persistent archival identifier (Zenodo or equivalent): **[INSERT DOI/ARCHIVAL ID]**
- Manuscript data/code availability statement: update with the final identifiers before submission.

## Branding

Before publication, add the approved USGS and Tulane University logo files and replace `[NEW LAB NAME TO BE CONFIRMED]` with the lab name approved by the authors and institutions. Do not add unofficial or modified institutional marks.

## Citation

Please cite the associated manuscript and, once deposited, the persistent archival release. A release-specific citation file should be added after the repository URL, version, authorship, and archival identifier are finalized.

## License and access review

No license is asserted by this preparation step. Before public release, the authors should confirm data-redistribution permissions, third-party terms, institutional branding approval, personally identifying information, API keys or credentials, and any restrictions attached to downloaded data.
