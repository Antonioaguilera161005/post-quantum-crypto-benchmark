# Benchmark Results

This document contains the main numerical results from the final benchmark campaign.

## Primitive key-establishment measurements

| Algorithm | Operation | Mean |
|---|---|---:|
| X25519 | keygen | 0.0492 ms |
| X25519 | exchange | 0.0399 ms |
| ML-KEM-512 | keygen | 0.0358 ms |
| ML-KEM-512 | encaps | 0.0440 ms |
| ML-KEM-512 | decaps | 0.0513 ms |
| ML-KEM-768 | keygen | 0.0608 ms |
| ML-KEM-768 | encaps | 0.0635 ms |
| ML-KEM-768 | decaps | 0.0727 ms |
| ML-KEM-1024 | keygen | 0.0781 ms |
| ML-KEM-1024 | encaps | 0.0870 ms |
| ML-KEM-1024 | decaps | 0.1014 ms |
| HKDF-SHA256 | derive | 0.0071 ms |

## Canonical key-establishment component model

| Scenario | Client | Server | Total | Transmitted |
|---|---:|---:|---:|---:|
| X25519 | 0.0892 ms | 0.0892 ms | 0.1783 ms | 64 B |
| ML-KEM-768 | 0.1335 ms | 0.0635 ms | 0.1970 ms | 2,272 B |
| X25519MLKEM768 | 0.2226 ms | 0.1526 ms | 0.3753 ms | 2,336 B |

## ML-KEM-768 vs X25519

Total compute ratio:

```text
1.1046×
```

95% bootstrap confidence interval:

```text
1.0029× – 1.2019×
```

Server-side compute ratio:

```text
0.7119×
```

95% bootstrap confidence interval:

```text
0.6410× – 0.7904×
```

The measured total-compute difference is modest.

Because X25519 and ML-KEM use different implementation stacks, this ratio should not be interpreted as a pure algorithm-only comparison.

## Derived hybrid result

The X25519MLKEM768 result is obtained by summing the measured X25519 and ML-KEM-768 component costs according to the RFC 10024 role assignment.

It is therefore not an independent timing measurement.

The derived model gives:

```text
0.3753 ms
```

Relative to X25519:

```text
2.1046×
```

Because the hybrid model contains the full X25519 work plus the ML-KEM component work, this ratio is mathematically related to the ML-KEM/X25519 ratio.

It should not be interpreted as a separate independent statistical observation.

## End-to-end hybrid diagnostic

The separate Python end-to-end diagnostic gives:

```text
0.4457 ms
```

Compared with:

```text
0.3753 ms
```

for the component model.

The diagnostic is approximately:

```text
18.8% higher
```

This difference includes additional Python wrapper and object-creation overhead.

The diagnostic result is therefore reported separately and is not used as the canonical TLS-oriented comparison.

## Traffic

Compared with the 64-byte X25519 baseline:

```text
ML-KEM-768:       35.5×
X25519MLKEM768:   36.5×
```

This is the largest relative change observed in the key-establishment comparison.

## Digital signatures

| Algorithm | Keygen | Sign | Verify | Public key | Signature |
|---|---:|---:|---:|---:|---:|
| ECDSA P-256 | 0.0343 ms | 0.0449 ms | 0.0982 ms | 65 B | ~71 B |
| ML-DSA-44 | 0.1060 ms | 0.4084 ms | 0.1112 ms | 1,312 B | 2,420 B |
| ML-DSA-65 | 0.1870 ms | 0.6314 ms | 0.1791 ms | 1,952 B | 3,309 B |
| ML-DSA-87 | 0.2996 ms | 0.7390 ms | 0.2777 ms | 2,592 B | 4,627 B |

## ML-DSA-44 vs ECDSA P-256

Signing ratio:

```text
9.0886×
```

95% bootstrap confidence interval:

```text
7.3856× – 10.7819×
```

Verification ratio:

```text
1.1327×
```

95% bootstrap confidence interval:

```text
1.0441× – 1.2201×
```

Public-key-size ratio:

```text
20.18×
```

Signature-size ratio:

```text
34.09×
```

## Operational impact

For 100 million key establishments per month:

| Scenario | Server CPU hours | Server egress |
|---|---:|---:|
| X25519 | 2.4764 h | 3.2 GB |
| ML-KEM-768 | 1.7631 h | 108.8 GB |
| X25519MLKEM768 | 4.2395 h | 112.0 GB |

Including both client and server cryptographic work:

| Scenario | Total CPU hours | Total cryptographic traffic |
|---|---:|---:|
| X25519 | 4.9529 h | 6.4 GB |
| ML-KEM-768 | 5.4710 h | 227.2 GB |
| X25519MLKEM768 | 10.4239 h | 233.6 GB |

## Key-establishment cloud model

For 100 million key establishments per month:

### Azure

| Scenario | Marginal total cost |
|---|---:|
| X25519 | $0.41/month |
| ML-KEM-768 | $9.56/month |
| X25519MLKEM768 | $9.97/month |

Hybrid extra cost versus classical:

```text
$9.56/month
$114.72/year
```

### GCP

| Scenario | Marginal total cost |
|---|---:|
| X25519 | $0.35/month |
| ML-KEM-768 | $8.68/month |
| X25519MLKEM768 | $9.03/month |

Hybrid extra cost versus classical:

```text
$8.68/month
$104.19/year
```

Under the assumptions of this model, direct cryptographic runtime cost remains small even at 100 million monthly key establishments.

The operational difference is driven mainly by transmitted cryptographic material rather than CPU cost.

## Signature cloud model

For 100 million signed operations per month:

### Azure

| Algorithm | Total modelled cost |
|---|---:|
| ECDSA P-256 | $0.68/month |
| ML-DSA-44 | $21.66/month |
| ML-DSA-65 | $29.73/month |
| ML-DSA-87 | $41.35/month |

### GCP

| Algorithm | Total modelled cost |
|---|---:|
| ECDSA P-256 | $0.61/month |
| ML-DSA-44 | $19.61/month |
| ML-DSA-65 | $26.89/month |
| ML-DSA-87 | $37.44/month |

These values depend on the configured pricing assumptions and traffic model.

They are not universal deployment-cost estimates.