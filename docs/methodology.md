# Benchmark Methodology

This document describes how the cryptographic measurements in this project are collected and how the final comparisons are constructed.

## Benchmark design

The final benchmark campaign uses:

- 10 independent runs;
- 100 warm-up iterations before measurement;
- 2,000 measured timing samples per operation and run;
- aggregation across independent run means;
- mean, median, p95, p99 and standard deviation measurements;
- coefficients of variation across independent runs.

The individual timing iterations inside a run are used to estimate the timing distribution of that run.

They are not treated as independent experimental replicates when calculating the final confidence intervals.

## Algorithms

### Key establishment

The benchmark covers:

- X25519;
- ML-KEM-512;
- ML-KEM-768;
- ML-KEM-1024;
- X25519MLKEM768;
- HKDF-SHA256.

ML-KEM-768 is used as the main post-quantum baseline because it corresponds to the ML-KEM parameter set used by the hybrid construction evaluated in the project.

### Digital signatures

The benchmark covers:

- ECDSA P-256;
- ML-DSA-44;
- ML-DSA-65;
- ML-DSA-87.

## Canonical key-establishment model

The main TLS comparison is not based on the Python end-to-end hybrid benchmark.

Instead, it is constructed from independently measured primitive operations.

For X25519, each side performs:

- one X25519 key generation;
- one X25519 key exchange.

For ML-KEM-768:

- the client performs ML-KEM key generation;
- the server performs ML-KEM encapsulation;
- the client performs ML-KEM decapsulation.

For X25519MLKEM768, the project follows the client/server role assignment used by RFC 10024:

### Client

- X25519 key generation;
- X25519 exchange;
- ML-KEM key generation;
- ML-KEM decapsulation.

### Server

- X25519 key generation;
- X25519 exchange;
- ML-KEM encapsulation.

The resulting hybrid secret is modelled as the concatenation of:

```text
ML-KEM shared secret || X25519 shared secret
```

HKDF is benchmarked separately.

It is not counted as a hybrid-specific cost because the TLS key schedule applies key derivation after group key agreement regardless of whether the selected group is classical or hybrid.

## Transmitted cryptographic material

The model counts the cryptographic material associated with the key-establishment construction.

### X25519

- client public key: 32 bytes;
- server public key: 32 bytes;
- total: 64 bytes.

### ML-KEM-768

- client public key: 1,184 bytes;
- server ciphertext: 1,088 bytes;
- total: 2,272 bytes.

### X25519MLKEM768

- client: 1,184-byte ML-KEM public key + 32-byte X25519 public key;
- server: 1,088-byte ML-KEM ciphertext + 32-byte X25519 public key;
- total: 2,336 bytes.

These values represent cryptographic material rather than complete serialized TLS records or network packets.

## Diagnostic hybrid benchmark

The repository also contains an end-to-end Python benchmark for the hybrid construction.

This measurement performs the complete construction through the Python wrapper.

It is retained as a diagnostic measurement only.

It is not used as the canonical TLS performance comparison because it includes additional effects such as:

- Python object creation;
- wrapper overhead;
- interpreter overhead;
- implementation-specific control flow.

The canonical comparison therefore uses measured primitive operations instead.

## Statistical treatment

Relative-performance confidence intervals are estimated using a non-parametric bootstrap over the 10 independent benchmark runs.

The procedure uses:

- 10,000 bootstrap resamples;
- a fixed random seed of `20261005`;
- paired run-level observations where the compared measurements originate from the same benchmark campaign.

The bootstrap unit is the independent run, not the individual timing sample.

The resulting intervals are stored in:

```text
results/raw/aggregated/bootstrap_confidence_intervals.csv
```

## Benchmark environment

The final campaign was executed using:

- CPU: AMD Ryzen 5 7520U with Radeon Graphics;
- OS: Windows x64;
- Python: 3.11.9;
- cryptography: 50.0.2;
- OpenSSL backend: OpenSSL 4.0.3;
- liboqs: 0.16.0;
- liboqs-python: 0.16.0.1;
- build type: Release;
- `OQS_DIST_BUILD`: enabled.

The recorded liboqs build also reports support for CPU extensions including:

- AES;
- AVX;
- AVX2;
- BMI1;
- BMI2;
- PCLMULQDQ;
- POPCNT;
- SSE;
- SSE2;
- SSE3.

Each run stores its environment metadata in:

```text
results/raw/runs/run_XX/environment.json
```

The benchmark campaign records the Git commit and whether the working tree was clean when the campaign started.

## Native liboqs cross-check

The Python benchmarks are complemented by the native liboqs speed executables.

The campaign runs:

```text
speed_kem
```

for ML-KEM-768 and:

```text
speed_sig
```

for ML-DSA-44.

The raw native outputs are stored in:

```text
results/native/
```

These measurements are used as an implementation-level cross-check rather than as replacements for the Python benchmark campaign.

## Limitations

The methodology has several intentional limits.

- The canonical hybrid comparison is component-based rather than a complete serialized TLS handshake.
- Full TLS framing, packetization and MTU effects are not modelled.
- TLS resumption is not included.
- CPU-hours are idealized serial CPU-hours rather than complete VM utilization measurements.
- Python benchmark results include wrapper overhead to varying degrees depending on the primitive.
- Results are specific to the benchmark machine, software versions and build configuration.