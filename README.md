# French MTPL data

This repository stores the French Motor Third-Party Liability frequency data as
`freMTPL2freq.csv`.

Run the dependency-free downloader from the repository root:

```bash
python3 download_fremtpl2freq.py
```

The script downloads OpenML data set 41214, converts its ARFF records to CSV,
and writes the result atomically. An existing CSV is retained unless `--force`
is supplied.

```bash
python3 download_fremtpl2freq.py --force
```
