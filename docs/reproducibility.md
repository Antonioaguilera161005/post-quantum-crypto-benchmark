# Reproducibility

This project separates hardware-dependent measurements from deterministic derived analysis.

## Reproduce the analysis

The committed raw benchmark runs are treated as experimental inputs.

Run:

```bash
python -m analysis.reproduce
```

This regenerates:

```text
aggregated ML-KEM results
aggregated X25519 results
aggregated HKDF results
hybrid diagnostic results
RFC 10024-oriented component model
signature aggregates
bootstrap confidence intervals
operational impact
provider compute costs
network costs
combined operational costs
signature cost analysis
migration scenarios
migration sensitivity results
```

To regenerate figures as well:

```bash
python -m analysis.reproduce --figures
```

This workflow is deterministic and is used by continuous integration.

## Run a new benchmark campaign

A new hardware-dependent campaign can be executed with:

```bash
python -m benchmarks.run_full_campaign
```

This launches:

```text
native ML-KEM cross-check
10 key-establishment runs
native ML-DSA cross-check
10 digital-signature runs
```

The key-establishment suite contains:

```text
ML-KEM
X25519
X25519MLKEM768 diagnostic
HKDF-SHA256
```

The signature suite contains:

```text
ECDSA P-256
ML-DSA
```

## Python environment

The committed campaign used Python 3.11.9.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## liboqs

The final Windows campaign used an explicit Release build of liboqs 0.16.0.

The installation path on the benchmark machine was:

```text
C:\Users\anton\_oqs_release
```

The loaded library was:

```text
C:\Users\anton\_oqs_release\bin\oqs.dll
```

The runtime environment can be configured with:

```powershell
$env:OQS_INSTALL_PATH = "$HOME\_oqs_release"
$env:Path = "$HOME\_oqs_release\bin;$env:Path"
```

The loaded native library can be checked with:

```powershell
python -c "import oqs; print(oqs.native()._name)"
```

These machine-specific paths are recorded as experimental provenance.

Future campaigns can normalize paths in generated metadata without changing the committed measurements from the original campaign.

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

The metadata is stored in:

```text
results/raw/runs/run_XX/environment.json
```

The final committed campaign started with:

```text
git_dirty_at_campaign_start = false
```

Both benchmark suites record the same campaign start time and Git commit.

## Power configuration

The final benchmark campaign was executed with the Windows:

```text
Balanced
```

power plan.

This is recorded in the environment metadata.

The machine is a low-power laptop, so the benchmark should not be interpreted as server-grade performance.

A dedicated Linux-server campaign would be a useful future comparison.

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

These files include the native liboqs configuration and operation timings.

They are used as implementation-level sanity checks rather than as replacements for the main benchmark campaign.

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

There is no separate top-level `results/raw/environment.json`.

Per-run environment records are the canonical provenance source.

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

The bootstrap CSV serializes floating-point values to six decimal places.

This avoids meaningless differences at approximately machine-precision scale from causing reproducibility checks to fail.

## Tests

Run:

```bash
python -m pytest
```

The current test suite contains 18 tests covering:

```text
hybrid construction
ML-KEM
digital signatures
X25519
```

## Continuous integration

GitHub Actions performs:

1. repository checkout;
2. Python setup;
3. liboqs setup;
4. dependency installation;
5. test execution;
6. deterministic result regeneration;
7. comparison with committed derived CSV outputs.

The CI does not rerun hardware benchmarks.

This separation is intentional.

Hardware timing results depend on:

- machine;
- operating system;
- power configuration;
- background load;
- compiled implementation.

Derived analysis from committed raw measurements should remain deterministic.

## Recommended verification workflow

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

A new benchmark campaign should ideally start from a clean Git working tree so the recorded provenance identifies the exact code used for the experiment.

## Current scope

The reproducibility pipeline covers the current component-level benchmark.

It does not yet include:

```text
native OpenSSL X25519 cross-checks
native OpenSSL ECDSA cross-checks
full TLS X25519MLKEM768 interoperability
serialized TLS KeyShare benchmarking
Linux server measurements
```

These are future extensions rather than requirements for reproducing the committed results.