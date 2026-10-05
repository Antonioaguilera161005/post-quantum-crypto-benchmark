# Reproducibility

This project separates hardware-dependent experimental measurements from deterministic derived analysis.

## Two levels of reproduction

There are two different workflows.

### 1. Reproduce the analysis

This uses the committed raw benchmark measurements as experimental inputs.

Run:

```bash
python -m analysis.reproduce
```

This regenerates:

- aggregated ML-KEM results;
- aggregated X25519 results;
- aggregated HKDF results;
- hybrid diagnostic results;
- canonical TLS key-establishment model;
- signature aggregates;
- bootstrap confidence intervals;
- operational impact;
- provider compute costs;
- network costs;
- combined operational costs;
- signature cost analysis;
- migration scenarios;
- migration sensitivity results.

To regenerate figures as well:

```bash
python -m analysis.reproduce --figures
```

This workflow is deterministic and is suitable for continuous integration.

## 2. Run a new benchmark campaign

A new campaign performs hardware-dependent measurements again.

Run:

```bash
python -m benchmarks.run_full_campaign
```

This launches:

1. native ML-KEM cross-check;
2. 10 key-establishment runs;
3. native ML-DSA cross-check;
4. 10 digital-signature runs.

The key-establishment suite includes:

```text
ML-KEM
X25519
X25519MLKEM768 diagnostic
HKDF-SHA256
```

The signature suite includes:

```text
ECDSA P-256
ML-DSA
```

## Python environment

The committed campaign used Python 3.11.9.

Create and activate a virtual environment before installing the project dependencies.

Example on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## liboqs

The final Windows campaign used an explicit Release build of liboqs 0.16.0.

The installation path was:

```text
C:\Users\anton\_oqs_release
```

The loaded library was:

```text
C:\Users\anton\_oqs_release\bin\oqs.dll
```

The environment can be configured in PowerShell with:

```powershell
$env:OQS_INSTALL_PATH = "$HOME\_oqs_release"
$env:Path = "$HOME\_oqs_release\bin;$env:Path"
```

The loaded native library can be checked with:

```powershell
python -c "import oqs; print(oqs.native()._name)"
```

## Benchmark provenance

At the start of the full campaign the runner records:

- UTC campaign start time;
- Git commit;
- whether the repository was dirty;
- CPU model;
- operating system;
- Python version;
- cryptography version;
- OpenSSL version;
- liboqs version;
- liboqs-python version;
- loaded liboqs library path;
- build configuration;
- OQS build flags;
- active CPU extensions;
- compiler;
- target platform;
- Windows power scheme.

The metadata is stored in each:

```text
results/raw/runs/run_XX/environment.json
```

The final committed campaign started from:

```text
git_dirty_at_campaign_start = false
```

Both benchmark suites also record the same campaign start timestamp and Git commit.

## Native cross-checks

A native liboqs benchmark is executed once per campaign for:

```text
ML-KEM-768
ML-DSA-44
```

Raw output is stored in:

```text
results/native/ml_kem_768_speed.txt
results/native/ml_dsa_44_speed.txt
```

These files include the native build configuration and measured operation timings.

## Raw data layout

Each independent benchmark run is stored under:

```text
results/raw/runs/run_01/
results/raw/runs/run_02/
...
results/raw/runs/run_10/
```

A typical run contains:

```text
ml_kem_benchmark.csv
x25519_benchmark.csv
hybrid_benchmark.csv
hkdf_benchmark.csv
ecdsa_benchmark.csv
ml_dsa_benchmark.csv
environment.json
```

Aggregated results are stored in:

```text
results/raw/aggregated/
```

## Statistical reproducibility

Bootstrap confidence intervals can be regenerated with:

```bash
python -m analysis.bootstrap_confidence_intervals
```

The analysis uses:

```text
Independent runs: 10
Bootstrap samples: 10,000
Random seed: 20261005
Bootstrap unit: independent run
```

Using a fixed seed makes the committed confidence-interval output reproducible.

## Tests

Run:

```bash
python -m pytest
```

The current test suite contains 18 tests covering:

- hybrid construction;
- ML-KEM;
- digital signatures;
- X25519.

## Continuous integration

GitHub Actions performs the following on supported pushes and pull requests:

1. checks out the repository;
2. prepares Python;
3. provides liboqs;
4. installs project dependencies;
5. executes the test suite;
6. regenerates deterministic derived results;
7. checks that committed derived CSV outputs do not change.

The CI does not rerun hardware benchmarks.

This separation is intentional.

Hardware timing results depend on the machine, operating system, background load and compiled implementation, while the analysis derived from committed raw measurements should be deterministic.

## Recommended reproduction workflow

To verify an existing commit:

```bash
python -m pytest
python -m analysis.reproduce
```

To execute a completely new experiment:

```bash
python -m benchmarks.run_full_campaign
python -m analysis.reproduce --figures
python -m pytest
```

A new hardware campaign should ideally begin from a clean Git working tree so that the recorded provenance clearly identifies the code used for the experiment.