# Post-Quantum Cryptography Benchmark & Migration Cost Analysis

Experimental study of the **technical and economic impact of migrating from classical cryptography to post-quantum cryptography (PQC)**.

The project benchmarks classical, post-quantum and hybrid cryptographic schemes, measures their computational and communication overhead, and translates those measurements into simplified cloud infrastructure and migration-cost models.

The goal is not only to answer:

> How much slower or larger is post-quantum cryptography?

but also:

> What does that difference mean for a real organization migrating its infrastructure?

---

## Overview

Two major cryptographic functions are analysed:

### Key establishment

- **X25519**
- **ML-KEM-512**
- **ML-KEM-768**
- **ML-KEM-1024**
- **Hybrid X25519 + ML-KEM-768**

### Digital signatures

- **ECDSA P-256**
- **ML-DSA-44**
- **ML-DSA-65**
- **ML-DSA-87**

The project evaluates:

- Key generation time
- Encapsulation / decapsulation
- Signing time
- Verification time
- Public-key size
- Ciphertext size
- Signature size
- Communication overhead
- Server CPU impact
- Cloud compute cost
- Cloud network cost
- Migration-cost sensitivity

---

# Motivation

Large-scale quantum computers would threaten widely deployed public-key cryptography based on integer factorization and discrete logarithms.

Post-quantum algorithms replace these assumptions with mathematical problems believed to remain difficult even for quantum computers.

However, migration is not free.

PQC algorithms introduce different:

- computation requirements,
- public-key sizes,
- ciphertext sizes,
- signature sizes,
- infrastructure requirements,
- compatibility constraints,
- deployment and testing costs.

This project studies those trade-offs experimentally.

---

# Architecture

```text
pqc-benchmark/
│
├── algorithms/
│   ├── classical/
│   │   ├── x25519.py
│   │   └── ecdsa_p256.py
│   │
│   ├── post_quantum/
│   │   ├── ml_kem.py
│   │   └── ml_dsa.py
│   │
│   └── hybrid/
│       └── x25519_mlkem768.py
│
├── benchmarks/
│   ├── benchmark_ml_kem.py
│   ├── benchmark_x25519.py
│   ├── benchmark_hybrid.py
│   ├── benchmark_hkdf.py
│   ├── benchmark_ecdsa.py
│   ├── benchmark_ml_dsa.py
│   ├── run_benchmark_suite.py
│   └── run_signature_suite.py
│
├── analysis/
│   ├── aggregate_benchmarks.py
│   ├── aggregate_signatures.py
│   ├── compare_key_establishment.py
│   └── generate_figures.py
│
├── cost_model/
│   ├── operational_impact.py
│   ├── cloud_network_cost.py
│   ├── cloud_compute_cost.py
│   ├── provider_compute_cost.py
│   ├── total_operational_cost.py
│   ├── migration_cost.py
│   ├── migration_sensitivity.py
│   └── signature_operational_impact.py
│
├── results/
│   ├── raw/
│   ├── economic/
│   └── figures/
│
└── tests/
```

---

# Methodology

Microbenchmarks are executed using:

- **100 warm-up iterations**
- **2,000 measured iterations**
- **10 independent benchmark runs**

This produces approximately:

```text
10 runs × 2,000 measurements
```

per primitive and operation.

Results are aggregated across runs.

The analysis includes:

- mean execution time,
- median,
- standard deviation,
- P95,
- P99,
- operations per second,
- coefficient of variation between runs.

This reduces the dependence of the results on a single benchmark execution.

---

# Key Establishment Results

Aggregated component-based results:

| Scheme | Crypto work | Transmitted material | Compute ratio vs X25519 | Traffic ratio |
|---|---:|---:|---:|---:|
| X25519 | 0.227 ms | 64 B | 1.0× | 1.0× |
| ML-KEM-768 | 1.573 ms | 2,272 B | 6.94× | 35.5× |
| X25519 + ML-KEM-768 | 1.815 ms | 2,336 B | 8.00× | 36.5× |

The hybrid construction combines both shared secrets using **HKDF-SHA256**.

```text
X25519 secret ──┐
                ├── HKDF-SHA256 ── Hybrid secret
ML-KEM secret ──┘
```

### Main observation

ML-KEM introduces significantly more cryptographic work and much larger protocol material than X25519.

However, this does **not** mean that a real network connection becomes 7–8× slower.

The measurements represent cryptographic computation only and exclude factors such as:

- network latency,
- TLS processing,
- application processing,
- certificates,
- database access,
- transport overhead.

![Key Establishment Performance](results/figures/key_establishment_compute.png)

![Key Establishment Size](results/figures/key_establishment_size.png)

---

# Digital Signature Results

Aggregated results:

| Scheme | Sign | Verify | Public key | Signature |
|---|---:|---:|---:|---:|
| ECDSA P-256 | 0.090 ms | 0.208 ms | 65 B | ~71 B |
| ML-DSA-44 | 5.833 ms | 1.555 ms | 1,312 B | 2,420 B |
| ML-DSA-65 | 8.816 ms | 2.370 ms | 1,952 B | 3,309 B |
| ML-DSA-87 | 10.601 ms | 3.751 ms | 2,592 B | 4,627 B |

In this experimental environment:

### ML-DSA-44

Signing:

```text
~64.6× ECDSA P-256
```

Verification:

```text
~7.5× ECDSA P-256
```

Signature size:

```text
~34× ECDSA P-256
```

The higher ML-DSA parameter sets introduce further computational and communication overhead.

![Signature Performance](results/figures/signature_performance.png)

![Signature Size](results/figures/signature_size.png)

![Public Key Size](results/figures/signature_public_key_size.png)

---

# Large-Scale Operational Impact

The measured primitive costs were extrapolated to large workloads.

For:

```text
100,000,000 operations / month
```

## Key establishment

Server-side cryptographic CPU usage:

| Scheme | Server CPU |
|---|---:|
| X25519 | 3.15 CPU-h |
| ML-KEM-768 | 29.03 CPU-h |
| Hybrid | 32.39 CPU-h |

Server cryptographic egress:

| Scheme | Egress |
|---|---:|
| X25519 | 3.2 GB |
| ML-KEM-768 | 118.4 GB |
| Hybrid | 121.6 GB |

Even though the relative overhead is large, the absolute CPU requirement remains relatively small at this scale.

---

# Digital Signature Operational Impact

For **100 million signed operations per month**:

| Algorithm | Signing CPU | Verification CPU | Signature traffic |
|---|---:|---:|---:|
| ECDSA P-256 | 2.51 h | 5.78 h | 7.1 GB |
| ML-DSA-44 | 162.0 h | 43.2 h | 242.0 GB |
| ML-DSA-65 | 244.9 h | 65.8 h | 330.9 GB |
| ML-DSA-87 | 294.5 h | 104.2 h | 462.7 GB |

Digital signatures therefore show a considerably larger operational impact than the ML-KEM key-establishment scenario.

---

# Cloud Cost Model

The project converts measured resource overhead into simplified cloud-cost estimates.

Two different network scenarios are used.

### Standalone

The cryptographic traffic is treated as the only traffic generated by the cloud account.

Provider free allowances may therefore apply.

### Marginal / Enterprise

The organization's existing infrastructure is assumed to have already consumed the free allowance.

The model therefore estimates the **incremental cost caused by PQC**.

---

## Key Establishment

At 100 million handshakes per month, the additional operational cost compared with X25519 was approximately:

| Provider | ML-KEM-768 | Hybrid |
|---|---:|---:|
| Azure | ~$11.41/month | ~$11.87/month |
| GCP | ~$10.14/month | ~$10.53/month |

Annual additional operational cost:

```text
approximately $120–142 / year
```

under the model assumptions.

![Key Establishment Cloud Cost](results/figures/key_establishment_cloud_cost.png)

---

# Signature Cloud Cost

For 100 million signed operations per month:

### Azure

| Scheme | Extra cost vs ECDSA |
|---|---:|
| ML-DSA-44 | ~$28.97/month |
| ML-DSA-65 | ~$41.14/month |
| ML-DSA-87 | ~$55.26/month |

### Google Cloud

| Scheme | Extra cost vs ECDSA |
|---|---:|
| ML-DSA-44 | ~$24.90/month |
| ML-DSA-65 | ~$35.22/month |
| ML-DSA-87 | ~$47.61/month |

![Signature Cloud Cost](results/figures/signature_cloud_cost.png)

---

# Migration Cost Model

Operational cryptographic overhead is only one component of a post-quantum migration.

The project also models:

```text
Crypto inventory
      +
Implementation
      +
Testing
      +
PKI integration
      +
Deployment
      +
Training
      +
HSM / infrastructure upgrades
```

Three hypothetical organization sizes are considered:

- Startup
- Mid-size
- Enterprise

These scenarios are **configurable assumptions**, not claims about actual market migration costs.

---

## Sensitivity Analysis

Current model output:

| Organization | Low | Central | High |
|---|---:|---:|---:|
| Startup | €7.8k | €11.5k | €20.7k |
| Mid-size | €75.7k | €116.1k | €204.5k |
| Enterprise | €662.8k | €1.013M | €1.787M |

![Migration Sensitivity](results/figures/migration_sensitivity.png)

The sensitivity model intentionally varies:

- engineering hours,
- engineering cost,
- HSM/infrastructure cost.

These values should be interpreted as **scenario analysis rather than externally validated predictions**.

---

# Main Finding

The experiments suggest an important distinction between **relative cryptographic overhead** and **absolute economic impact**.

Post-quantum algorithms can introduce very large relative changes:

```text
ML-KEM-768:
~6.9× cryptographic work
~35.5× communication material

ML-DSA-44:
~64.6× signing time
~34× signature size
```

However, the direct cloud infrastructure cost associated purely with cryptographic CPU and network overhead can remain relatively small.

This suggests the following hypothesis:

> The dominant economic challenge of post-quantum migration may lie less in executing PQC algorithms and more in discovering, modifying, testing and deploying cryptographic dependencies across large systems.

The migration-cost section of this project is designed to investigate this hypothesis.

---

# Reproducibility

All benchmark results are stored as raw CSV files.

Each run is stored independently:

```text
results/raw/runs/run_01/
results/raw/runs/run_02/
...
results/raw/runs/run_10/
```

Aggregated results are stored in:

```text
results/raw/aggregated/
```

This makes it possible to inspect both individual runs and aggregated measurements.

---

# Running the Project

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the key-establishment benchmark suite:

```powershell
python -m benchmarks.run_benchmark_suite
```

Aggregate results:

```powershell
python -m analysis.aggregate_benchmarks
```

Run signature benchmarks:

```powershell
python -m benchmarks.run_signature_suite
```

Aggregate signature results:

```powershell
python -m analysis.aggregate_signatures
```

Generate figures:

```powershell
python -m analysis.generate_figures
```

---

# Technologies

- Python
- Open Quantum Safe / liboqs
- ML-KEM
- ML-DSA
- X25519
- ECDSA P-256
- HKDF-SHA256
- `cryptography`
- pandas
- matplotlib

---

# Limitations

The results should not be interpreted as universal performance measurements.

Performance depends on:

- CPU architecture,
- operating system,
- compiler,
- cryptographic backend,
- library version,
- processor frequency,
- background workloads,
- implementation optimizations.

The current experiments were performed on a single local Windows system.

The cloud-cost models are simplified analytical models based on measured cryptographic resource consumption.

They do not represent complete:

- TLS traffic,
- VM utilization,
- application workloads,
- enterprise infrastructure,
- commercial discounts,
- personnel costs,
- real migration contracts.

Migration-cost scenarios are configurable assumptions and should not be interpreted as externally validated market estimates.

---

# Future Work

Planned extensions include:

- Certificate and PKI size analysis
- Hybrid digital signatures
- TLS handshake simulation
- PQC certificate chains
- Additional cloud providers
- Hardware benchmarking
- Linux benchmarking
- Automated statistical confidence intervals
- Crypto-agility migration analysis
- Real-world migration case studies

---

## Author

**Antonio Aguilera Slavcheva**

Mathematical Engineering student interested in cryptography, post-quantum cryptography and security research.