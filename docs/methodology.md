# Benchmark Methodology

This document describes how the cryptographic measurements are collected and how the final comparisons are constructed.

## Benchmark design

The final benchmark campaign uses:

- 10 independent runs;
- 100 warm-up iterations before measurement;
- 2,000 measured timing samples per operation and run;
- aggregation across independent run means;
- mean, median, p95, p99 and standard deviation measurements;
- coefficients of variation across independent runs.

The individual timing iterations inside a run describe the timing distribution of that run.

They are not treated as independent experimental replicates when calculating confidence intervals.

## Algorithms

### Key establishment

The benchmark covers:

- X25519;
- ML-KEM-512;
- ML-KEM-768;
- ML-KEM-1024;
- X25519MLKEM768;
- HKDF-SHA256.

ML-KEM-768 is the main post-quantum baseline because it corresponds to the ML-KEM parameter set used by the hybrid construction evaluated in the project.

### Digital signatures

The benchmark covers:

- ECDSA P-256;
- ML-DSA-44;
- ML-DSA-65;
- ML-DSA-87.

## RFC 10024-oriented key-establishment model

The canonical hybrid comparison is not a measured complete TLS handshake.

It is a component model constructed from independently measured primitive operations.

### X25519

Each side performs:

- one X25519 key generation;
- one X25519 key exchange.

### ML-KEM-768

The role assignment is:

- client: ML-KEM key generation;
- server: ML-KEM encapsulation;
- client: ML-KEM decapsulation.

### X25519MLKEM768

The model follows the client/server operation assignment defined for X25519MLKEM768 in RFC 10024.

Client work:

- X25519 key generation;
- X25519 exchange;
- ML-KEM key generation;
- ML-KEM decapsulation.

Server work:

- X25519 key generation;
- X25519 exchange;
- ML-KEM encapsulation.

The resulting hybrid secret is modelled as:

```text
ML-KEM shared secret || X25519 shared secret
```

Because the hybrid total is constructed as the sum of X25519 and ML-KEM component costs, the hybrid ratio is a **derived result** rather than an additional independent timing measurement.

## HKDF

HKDF-SHA256 is benchmarked independently.

It is not counted as a hybrid-specific operation because the TLS key schedule applies key derivation after group key agreement regardless of whether the selected group is classical or hybrid.

## Transmitted cryptographic material

The model counts the cryptographic material associated with each key-establishment construction.

### X25519

```text
Client public key: 32 bytes
Server public key: 32 bytes
Total: 64 bytes
```

### ML-KEM-768

```text
Client public key: 1,184 bytes
Server ciphertext: 1,088 bytes
Total: 2,272 bytes
```

### X25519MLKEM768

```text
Client:
1,184-byte ML-KEM public key
+ 32-byte X25519 public key

Server:
1,088-byte ML-KEM ciphertext
+ 32-byte X25519 public key

Total: 2,336 bytes
```

These values represent cryptographic material.

They do not represent complete serialized TLS records or network packets.

## Diagnostic hybrid benchmark

The repository also contains a Python end-to-end benchmark for the hybrid construction.

The final campaign measured:

```text
0.4457 ms
```

The component model gives:

```text
0.3753 ms
```

The end-to-end diagnostic is therefore approximately **18.8% higher**.

This difference includes effects that are not present when isolated primitive timings are simply added, including Python wrapper execution, object creation and additional control flow.

For that reason:

- the component model is used for the RFC 10024-oriented comparison;
- the Python end-to-end value is retained as a diagnostic result;
- the two values are not treated as equivalent measurements.

## Statistical treatment

Relative-performance confidence intervals are estimated using a non-parametric bootstrap over the 10 independent benchmark runs.

The procedure uses:

- 10,000 bootstrap resamples;
- a fixed random seed of `20261005`;
- paired run-level observations where compared measurements originate from the same benchmark campaign.

The bootstrap unit is the independent run, not the individual timing sample.

The resulting intervals are stored in:

```text
results/raw/aggregated/bootstrap_confidence_intervals.csv
```

Floating-point output in this CSV is serialized to six decimal places so that numerically irrelevant platform-level differences do not cause reproducibility checks to fail.

## Benchmark environment

The final campaign was executed using:

```text
CPU: AMD Ryzen 5 7520U with Radeon Graphics
OS: Windows x64
Python: 3.11.9
cryptography: 50.0.2
OpenSSL backend: OpenSSL 4.0.3
liboqs: 0.16.0
liboqs-python: 0.16.0.1
Build type: Release
OQS_DIST_BUILD: enabled
```

The recorded liboqs build reports active CPU extensions including:

```text
ADX
AES
AVX
AVX2
BMI1
BMI2
PCLMULQDQ
POPCNT
SSE
SSE2
SSE3
```

The final campaign was executed with the Windows **Balanced** power plan.

The benchmark machine is a low-power laptop rather than a dedicated server.

The timing results should therefore be interpreted as measurements of this specific environment, not as universal server-performance values.

There is also an implementation-stack difference in the classical/PQ comparison:

```text
ML-KEM -> liboqs -> liboqs-python
X25519 -> OpenSSL -> cryptography
```

Relative ratios therefore capture both algorithmic effects and implementation-stack effects.

## Environment provenance

Each run stores environment metadata under:

```text
results/raw/runs/run_XX/environment.json
```

The recorded information includes:

- CPU model;
- operating system;
- Python version;
- cryptography version;
- OpenSSL version;
- liboqs version;
- liboqs-python version;
- loaded liboqs library;
- build configuration;
- OQS build flags;
- active CPU extensions;
- compiler;
- target platform;
- power scheme;
- campaign start time;
- Git commit;
- Git working-tree state at campaign start.

The final committed campaign began with:

```text
git_dirty_at_campaign_start = false
```

## Native liboqs cross-check

The Python benchmark campaign is complemented by the native liboqs speed executables.

The campaign runs:

```text
speed_kem
```

for ML-KEM-768 and:

```text
speed_sig
```

for ML-DSA-44.

The raw outputs are stored under:

```text
results/native/
```

These measurements are implementation-level cross-checks.

They are not used as replacements for the Python benchmark campaign.

## Limitations

The methodology intentionally has a limited scope.

The project does not currently measure:

- complete serialized TLS handshakes;
- real client/server interoperability;
- full TLS framing;
- packetization;
- MTU effects;
- TLS resumption;
- network latency;
- production VM scheduling;
- multi-core scaling.

The current classical and post-quantum primitives also use different implementation stacks, so very small timing differences should be interpreted cautiously.