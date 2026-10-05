# Post-Quantum Cryptography Benchmark & Migration Cost Analysis

A reproducible benchmark comparing classical, post-quantum and hybrid cryptographic constructions, with an additional model of their operational and migration costs.

The project focuses on two questions:

1. What changes in compute time and transmitted data when moving from classical cryptography to post-quantum cryptography?
2. What could those differences mean operationally for a company processing cryptographic workloads at scale?

The benchmark covers:

- **X25519**
- **ML-KEM-512 / 768 / 1024**
- **X25519MLKEM768**, following the role assignment defined in RFC 10024
- **ECDSA P-256**
- **ML-DSA-44 / 65 / 87**

---

## Key findings

| Comparison | Result |
|---|---:|
| ML-KEM-768 vs X25519 | **1.10×** total cryptographic work |
| 95% bootstrap CI | **1.00× – 1.20×** |
| X25519MLKEM768 vs X25519 | **2.10×** total cryptographic work |
| 95% bootstrap CI | **2.00× – 2.20×** |
| ML-KEM-768 server compute | **0.71×** X25519 |
| Hybrid server compute | **1.71×** X25519 |
| ML-KEM-768 transmitted material | **35.5×** X25519 |
| Hybrid transmitted material | **36.5×** X25519 |
| ML-DSA-44 signing | **9.09×** ECDSA P-256 |
| ML-DSA-44 verification | **1.13×** ECDSA P-256 |
| ML-DSA-44 public key size | **20.18×** ECDSA P-256 |
| ML-DSA-44 signature size | **34.09×** ECDSA P-256 |

In this benchmark environment, ML-KEM-768 showed a modest total compute
overhead relative to X25519.

The hybrid X25519MLKEM768 construction required approximately twice the
total cryptographic work of X25519.

The larger operational difference came from **transmitted cryptographic
material rather than CPU time**.

![Key-establishment benchmark](results/figures/key_establishment_compute.png)

---

## Key-establishment results

The canonical comparison models the client and server work separately.

| Scenario | Client crypto | Server crypto | Total | Transmitted |
|---|---:|---:|---:|---:|
| X25519 | 0.0892 ms | 0.0892 ms | 0.1783 ms | 64 B |
| ML-KEM-768 | 0.1335 ms | 0.0635 ms | 0.1970 ms | 2,272 B |
| X25519MLKEM768 | 0.2226 ms | 0.1526 ms | 0.3753 ms | 2,336 B |

ML-KEM-768 alone is included as a conceptual PQ-only baseline.

The hybrid construction follows the client/server role assignment used by
**X25519MLKEM768 in RFC 10024**.

The separate end-to-end Python hybrid benchmark is retained as a diagnostic
measurement and is not used as the canonical TLS performance result.

---

## Digital signatures

| Algorithm | Sign | Verify | Public key | Signature |
|---|---:|---:|---:|---:|
| ECDSA P-256 | 0.0449 ms | 0.0982 ms | 65 B | ~71 B |
| ML-DSA-44 | 0.4084 ms | 0.1112 ms | 1,312 B | 2,420 B |
| ML-DSA-65 | 0.6314 ms | 0.1791 ms | 1,952 B | 3,309 B |
| ML-DSA-87 | 0.7390 ms | 0.2777 ms | 2,592 B | 4,627 B |

For ML-DSA-44:

- signing ratio vs ECDSA P-256: **9.09×**
- 95% bootstrap CI: **7.39× – 10.78×**
- verification ratio: **1.13×**
- 95% bootstrap CI: **1.04× – 1.22×**

---

## Operational cost model

The benchmark results are also translated into simplified cloud-resource
scenarios.

For **100 million key establishments per month**, the hybrid construction
produces:

| Provider | Classical | Hybrid | Extra vs classical |
|---|---:|---:|---:|
| Azure | $0.41/month | $9.97/month | **$9.56/month** |
| GCP | $0.35/month | $9.03/month | **$8.68/month** |

For **100 million signed operations per month**, ML-DSA-44 produces:

| Provider | ECDSA P-256 | ML-DSA-44 | Extra |
|---|---:|---:|---:|
| Azure | $0.68/month | $21.66/month | **$20.98/month** |
| GCP | $0.61/month | $19.61/month | **$18.99/month** |

These values are **model outputs**, not universal cloud-cost estimates.

Pricing, traffic assumptions and migration assumptions are configurable.

---

## Benchmark methodology

The committed benchmark campaign uses:

- **10 independent runs**
- **100 warm-up iterations** per operation
- **2,000 measured timing samples** per operation and run
- aggregation across independent run means
- run-level coefficients of variation
- **10,000 non-parametric bootstrap resamples**
- paired run-level bootstrap comparisons
- fixed bootstrap seed for reproducibility

Individual timing iterations are not treated as independent experimental
replicates when calculating the confidence intervals.

The final benchmark campaign was executed using:

- Python 3.11.9
- liboqs 0.16.0
- liboqs-python 0.16.0.1
- Release build
- `OQS_DIST_BUILD`
- AMD Ryzen 5 7520U
- Windows x64

Native `liboqs` speed binaries are also executed once per benchmark campaign
as an implementation-level cross-check.

Full methodology:

**[docs/methodology.md](docs/methodology.md)**

---

## Reproducing the results

The committed raw benchmark runs are treated as experimental inputs.

All deterministic statistical analyses and economic models can be regenerated
with:

```bash
python -m analysis.reproduce
```

To regenerate the figures as well:

```bash
python -m analysis.reproduce --figures
```

Run the test suite with:

```bash
python -m pytest
```

A completely new hardware-dependent benchmark campaign can be launched with:

```bash
python -m benchmarks.run_full_campaign
```

Raw benchmark measurements are intentionally not regenerated by CI because
timing results depend on the machine and runtime environment.

More details:

**[docs/reproducibility.md](docs/reproducibility.md)**

---

## Project structure

```text
algorithms/
    classical/
    post_quantum/
    hybrid/

benchmarks/
    primitive benchmarks
    benchmark suites
    environment capture
    full campaign runner

analysis/
    aggregation
    TLS key-establishment model
    bootstrap confidence intervals
    figure generation
    reproduction pipeline

cost_model/
    operational impact
    provider compute/network costs
    migration scenarios

results/
    raw/
        runs/
        aggregated/
    native/
    economic/
    figures/

tests/
docs/
```

---

## Documentation

Detailed documentation has been separated from the main README:

- **[Methodology](docs/methodology.md)** — benchmark design, RFC 10024 model and statistical treatment
- **[Results](docs/results.md)** — complete benchmark and confidence-interval results
- **[Economic model](docs/economic_model.md)** — operational and migration cost assumptions
- **[Reproducibility](docs/reproducibility.md)** — environment, commands, raw data and CI

---

## Important limitations

This project is a benchmark and modelling exercise, not a complete TLS
deployment study.

In particular:

- the canonical hybrid result is component-based rather than a full serialized
  TLS handshake benchmark;
- the Python end-to-end hybrid measurement includes wrapper and object-creation
  overhead and is therefore treated only as diagnostic;
- network calculations model cryptographic payload sizes rather than complete
  packets and protocol overhead;
- TLS resumption is not included;
- signature traffic does not currently include certificate-chain distribution;
- cloud costs are simplified resource models rather than complete VM bills;
- provider pricing tiers are not intended as a direct provider ranking;
- migration costs are hypothetical configurable scenarios, not empirical
  estimates of real company migrations.

---

## Why this project exists

Post-quantum migration is often discussed only in terms of algorithmic
security.

This project looks at a different part of the problem: what changes when those
algorithms have to be executed, transmitted and deployed in real systems.

The goal is not to predict a universal migration cost, but to provide a
reproducible framework where cryptographic measurements can be connected to
explicit operational assumptions.

---

## Author

**Antonio Aguilera Slavcheva**

Mathematical Engineering student interested in applied cryptography,
post-quantum cryptography and security research.

GitHub: [Antonioaguilera161005](https://github.com/Antonioaguilera161005)

---

## License

MIT License.