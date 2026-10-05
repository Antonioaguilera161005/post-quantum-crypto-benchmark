# Post-Quantum Cryptography Benchmark & Migration Cost Analysis

[![Tests and Reproducibility](https://github.com/Antonioaguilera161005/post-quantum-crypto-benchmark/actions/workflows/tests.yml/badge.svg)](https://github.com/Antonioaguilera161005/post-quantum-crypto-benchmark/actions/workflows/tests.yml)

A reproducible benchmark comparing classical, post-quantum and hybrid cryptographic constructions, together with a simplified model of their operational and migration costs.

The project focuses on two questions:

1. What changes in compute time and transmitted data when moving from classical cryptography to post-quantum cryptography?
2. What could those differences mean operationally for a company processing cryptographic workloads at scale?

The benchmark covers:

- X25519
- ML-KEM-512 / 768 / 1024
- X25519MLKEM768
- ECDSA P-256
- ML-DSA-44 / 65 / 87
- HKDF-SHA256

---

## Key findings

| Comparison | Result |
|---|---:|
| ML-KEM-768 vs X25519 | **1.10×** total cryptographic work |
| 95% bootstrap CI | **1.00× – 1.20×** |
| X25519MLKEM768 vs X25519 | **2.10× derived total cryptographic work** |
| ML-KEM-768 server compute | **0.71×** X25519 |
| Hybrid server compute | **1.71×** X25519 |
| ML-KEM-768 transmitted material | **35.5×** X25519 |
| Hybrid transmitted material | **36.5×** X25519 |
| ML-DSA-44 signing | **9.09×** ECDSA P-256 |
| ML-DSA-44 verification | **1.13×** ECDSA P-256 |
| ML-DSA-44 public key size | **20.18×** ECDSA P-256 |
| ML-DSA-44 signature size | **34.09×** ECDSA P-256 |

In this benchmark environment, ML-KEM-768 showed a modest total compute overhead relative to X25519.

The X25519MLKEM768 value is a **derived component-model result**, not an independent end-to-end TLS measurement. By construction, the hybrid model adds the measured X25519 work to the measured ML-KEM-768 work.

The separate Python end-to-end hybrid diagnostic measured **0.4457 ms**, compared with **0.3753 ms** for the component model, about **18.8% higher**. This diagnostic includes wrapper, object-creation and other end-to-end Python overhead, so it is reported separately rather than used as the canonical comparison.

The largest difference in the benchmark is not CPU time but transmitted cryptographic material.

![Key-establishment benchmark](results/figures/key_establishment_compute.png)

---

## Key-establishment results

The main comparison is an RFC 10024-oriented component model with client and server work separated.

| Scenario | Client crypto | Server crypto | Total | Transmitted |
|---|---:|---:|---:|---:|
| X25519 | 0.0892 ms | 0.0892 ms | 0.1783 ms | 64 B |
| ML-KEM-768 | 0.1335 ms | 0.0635 ms | 0.1970 ms | 2,272 B |
| X25519MLKEM768 | 0.2226 ms | 0.1526 ms | 0.3753 ms | 2,336 B |

ML-KEM-768 alone is included as a conceptual PQ-only baseline.

For X25519MLKEM768, the client/server operation assignment follows RFC 10024:

- the client performs ML-KEM key generation and decapsulation;
- the server performs ML-KEM encapsulation;
- both sides perform X25519 operations.

The hybrid result is obtained by summing the measured primitive costs for those operations.

It should therefore be interpreted as a **TLS-oriented component model**, not as a measured complete TLS handshake.

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

The benchmark results are translated into simplified cloud-resource scenarios.

For **100 million key establishments per month**:

| Provider | Classical | Hybrid | Extra vs classical |
|---|---:|---:|---:|
| Azure | $0.41/month | $9.97/month | **$9.56/month** |
| GCP | $0.35/month | $9.03/month | **$8.68/month** |

For **100 million signed operations per month** using ML-DSA-44:

| Provider | ECDSA P-256 | ML-DSA-44 | Extra |
|---|---:|---:|---:|
| Azure | $0.68/month | $21.66/month | **$20.98/month** |
| GCP | $0.61/month | $19.61/month | **$18.99/month** |

Under these assumptions, the direct cryptographic runtime cost is small even at 100 million key establishments per month.

The larger practical concern is therefore not raw CPU cost, but increased transmitted data and the engineering effort required to migrate existing systems.

The migration-cost scenarios in this repository are hypothetical and should not be interpreted as empirical estimates of real company migrations.

---

## Benchmark methodology

The committed benchmark campaign uses:

- 10 independent runs
- 100 warm-up iterations per operation
- 2,000 measured timing samples per operation and run
- aggregation across independent run means
- run-level coefficients of variation
- 10,000 non-parametric bootstrap resamples
- paired run-level comparisons
- a fixed bootstrap seed for reproducibility

Individual timing iterations are not treated as independent experimental replicates when calculating confidence intervals.

The final benchmark campaign was executed using:

- Python 3.11.9
- liboqs 0.16.0
- liboqs-python 0.16.0.1
- Release build
- `OQS_DIST_BUILD`
- AMD Ryzen 5 7520U
- Windows x64

Native liboqs speed binaries are also executed once per benchmark campaign as an implementation-level cross-check.

Full methodology:

**[docs/methodology.md](docs/methodology.md)**

---

## Reproducing the results

The committed raw benchmark runs are treated as experimental inputs.

All deterministic statistical analyses and economic models can be regenerated with:

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

Raw hardware timing measurements are intentionally not regenerated by CI because they depend on the machine and runtime environment.

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
    RFC 10024-oriented component model
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

Detailed documentation is kept outside the main README:

- **[Methodology](docs/methodology.md)** — benchmark design, component model and statistical treatment
- **[Results](docs/results.md)** — complete benchmark and confidence-interval results
- **[Economic model](docs/economic_model.md)** — operational and migration cost assumptions
- **[Reproducibility](docs/reproducibility.md)** — environment, commands, raw data and CI

---

## Important limitations

This project is a benchmark and modelling exercise, not a complete TLS deployment study.

In particular:

- the canonical hybrid result is a derived component model rather than a complete serialized TLS handshake measurement;
- the Python end-to-end hybrid diagnostic includes wrapper and object-creation overhead;
- the model counts cryptographic material rather than complete TLS records or network packets;
- TLS resumption is not included;
- packet fragmentation and MTU effects are not modelled;
- signature traffic does not include certificate-chain distribution;
- cloud costs are simplified resource models rather than complete VM bills;
- provider pricing tiers are not intended as a direct provider comparison;
- migration costs are hypothetical configurable scenarios;
- ML-KEM is benchmarked through liboqs/liboqs-python, while X25519 uses cryptography/OpenSSL, so relative timings include implementation-stack differences as well as algorithmic differences;
- the final campaign was executed on a low-power laptop using the Windows **Balanced** power plan, so timings should not be treated as server-grade performance measurements.

---

## Main conclusion

Under the assumptions used here, the direct CPU and cloud-runtime cost of post-quantum key establishment is small.

The clearest measurable change is data size: ML-KEM-768 and X25519MLKEM768 transmit roughly **35–36× more cryptographic material** than the X25519 baseline.

For a real organization, the harder problem is therefore likely to be migration engineering, interoperability, deployment and protocol integration rather than raw cryptographic CPU cost.

---

## Future work

Possible extensions include:

- native OpenSSL cross-checks for X25519 and ECDSA;
- measurements on a dedicated Linux server;
- serialized TLS `KeyShare` measurements;
- full TLS interoperability testing with X25519MLKEM768;
- certificate-chain modelling for ML-DSA;
- TLS resumption scenarios;
- packet and MTU-level network analysis.

---

## Author

**Antonio Aguilera Slavcheva**

Mathematical Engineering student interested in applied cryptography, post-quantum cryptography and security research.

GitHub: [Antonioaguilera161005](https://github.com/Antonioaguilera161005)

---

## License

MIT License.