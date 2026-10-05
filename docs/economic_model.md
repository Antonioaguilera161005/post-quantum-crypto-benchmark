# Economic Model

The economic part of this project translates measured cryptographic resource use into simplified operational and migration-cost scenarios.

It does not attempt to predict the exact cost of a production PQC migration.

Its purpose is to connect measured cryptographic costs to explicit, reproducible assumptions.

## Operational model

The operational model starts from:

- measured cryptographic timings;
- transmitted cryptographic bytes;
- configured provider compute prices;
- configured provider network prices.

For key establishment, the model estimates:

- server cryptographic CPU-hours;
- server outbound cryptographic traffic;
- compute cost;
- network cost;
- incremental cost relative to X25519.

The main scenarios are:

```text
X25519
ML-KEM-768
X25519MLKEM768
```

ML-KEM-768 alone is retained as a conceptual PQ-only baseline.

## CPU-hours

For a workload of `N` operations per month:

```text
CPU-hours =
    operation_time_ms
    × N
    / 1000
    / 3600
```

These are equivalent serial CPU-hours.

They are not complete VM utilization or wall-clock estimates.

## Network model

Only server outbound cryptographic material is charged in the key-establishment company-cost model.

The model distinguishes two cases.

### Standalone

The cryptographic workload can use the provider's configured free network allowance.

### Marginal

The provider's free allowance is assumed to have already been consumed by normal business traffic.

All additional cryptographic traffic is therefore charged.

The main README uses the marginal model because it represents the incremental cost of changing the cryptographic construction in an existing workload.

## Provider assumptions

Pricing inputs are stored in:

```text
cost_model/config/cloud_pricing.csv
```

The current model includes:

```text
Azure compute
Azure network
GCP compute
GCP network
AWS compute
```

AWS is not included in the final combined operational-cost comparison because AWS network egress has not yet been modelled.

The pricing assumptions used in the current committed outputs were checked on:

```text
2026-10-04
```

Provider prices are modelling inputs and may change.

## 100 million key establishments per month

The final campaign produces:

| Scenario | Server CPU hours/month | Server egress/month |
|---|---:|---:|
| X25519 | 2.4764 h | 3.2 GB |
| ML-KEM-768 | 1.7631 h | 108.8 GB |
| X25519MLKEM768 | 4.2395 h | 112.0 GB |

The hybrid construction therefore adds limited compute cost but substantially more transmitted cryptographic material.

## Combined operational cost

Using the current configured pricing:

### Azure

```text
X25519:             $0.41/month
ML-KEM-768:         $9.56/month
X25519MLKEM768:     $9.97/month
```

Hybrid incremental cost:

```text
$9.56/month
$114.72/year
```

### GCP

```text
X25519:             $0.35/month
ML-KEM-768:         $8.68/month
X25519MLKEM768:     $9.03/month
```

Hybrid incremental cost:

```text
$8.68/month
$104.19/year
```

Under these assumptions, the direct runtime cost is small.

The main operational effect is increased network traffic rather than cryptographic CPU consumption.

## Signature operational model

For digital signatures, the company is assumed to perform the signing operation.

The model includes:

- signing CPU;
- signature bytes as outbound traffic.

Verification CPU is reported for context but excluded from company cost because verification is assumed to occur on the client side.

The current model does not charge public-key or certificate-chain distribution once per signature.

For 100 million signed operations per month:

### Azure

```text
ECDSA P-256:   $0.68/month
ML-DSA-44:    $21.66/month
ML-DSA-65:    $29.73/month
ML-DSA-87:    $41.35/month
```

### GCP

```text
ECDSA P-256:   $0.61/month
ML-DSA-44:    $19.61/month
ML-DSA-65:    $26.89/month
ML-DSA-87:    $37.44/month
```

The larger post-quantum signature sizes are responsible for most of the modelled cost increase.

## Migration-cost scenarios

The repository also contains a configurable one-time migration model.

The central scenarios are:

| Scenario | Engineering hours | HSM upgrade | Total |
|---|---:|---:|---:|
| Startup | 192 h | $0 | $11,520 |
| Mid-size | 1,348 h | $15,000 | $116,100 |
| Enterprise | 9,400 h | $120,000 | $1,013,000 |

These values are hypothetical scenario assumptions.

They are not empirical estimates of what a real organization will pay.

The model represents possible categories of work such as:

- implementation;
- testing;
- deployment;
- infrastructure changes;
- HSM replacement or upgrades.

## Sensitivity analysis

Each migration scenario has low, central and high cases.

### Startup

```text
Low:       $7,776
Central:  $11,520
High:     $20,736
```

### Mid-size

```text
Low:       $75,742.50
Central:  $116,100
High:     $204,480
```

### Enterprise

```text
Low:       $662,775
Central: $1,013,000
High:    $1,787,400
```

The `idealized_parallel_months` field assumes perfect parallelism and 160 productive engineering hours per engineer per month.

It should not be interpreted as a prediction of real calendar migration duration.

## Interpretation

The operational outputs are modest compared with the hypothetical migration scenarios.

That does not mean real migration costs are known.

It means that, under this model, direct cryptographic runtime cost is unlikely to be the dominant concern.

Real deployments are more likely to be affected by:

- engineering work;
- interoperability;
- infrastructure compatibility;
- certificate and key-management changes;
- procurement;
- vendor support;
- staged deployment.

## Limitations

The economic model intentionally simplifies real infrastructure.

It does not currently model:

- complete VM billing;
- autoscaling;
- reserved capacity;
- enterprise discounts;
- TLS resumption;
- packet-level overhead;
- MTU fragmentation;
- complete certificate-chain traffic;
- multi-region traffic;
- engineering dependencies;
- procurement delays;
- vendor delays;
- production rollout schedules.

Azure and GCP also use different pricing structures.

The outputs should therefore not be interpreted as a controlled provider ranking.

The useful result is the framework and the order of magnitude under explicit assumptions, not a universal cost forecast.