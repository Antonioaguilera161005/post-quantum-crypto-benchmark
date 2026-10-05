# Economic Model

The economic part of this project translates measured cryptographic resource use into simplified operational and migration-cost scenarios.

It is not intended to predict the exact cost of a production PQC migration.

Its purpose is to make the assumptions explicit and reproducible.

## Operational cost model

The operational model starts from measured cryptographic timings and transmitted bytes.

For key establishment, the model estimates:

- server cryptographic CPU-hours;
- server outbound cryptographic traffic;
- reference compute cost;
- reference network cost.

The main scenarios are:

- classical X25519;
- conceptual PQ-only ML-KEM-768;
- hybrid X25519MLKEM768.

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

They are not intended to represent exact VM wall-clock consumption or complete infrastructure utilization.

## Network model

Only server outbound cryptographic material is charged in the key-establishment company-cost model.

The model distinguishes two cases.

### Standalone

The cryptographic workload can use the provider's configured free network allowance.

### Marginal

The provider's free allowance is assumed to have already been consumed by normal business traffic.

All additional cryptographic traffic is therefore charged.

The main README uses the marginal model because it better represents the incremental cost of changing the cryptographic construction in an existing workload.

## Provider assumptions

Pricing inputs are stored in:

```text
cost_model/config/cloud_pricing.csv
```

The current model includes:

- Azure compute;
- Azure network;
- GCP compute;
- GCP network;
- AWS compute.

AWS is not included in the final combined operational-cost comparison because an AWS network-egress model has not been added.

The pricing inputs used in the current committed results were checked on:

```text
2026-10-04
```

Provider prices are modelling inputs and can change over time.

## 100 million key establishments per month

The final benchmark campaign produces the following server-side resource estimates:

| Scenario | CPU hours/month | Egress/month |
|---|---:|---:|
| X25519 | 2.4764 h | 3.2 GB |
| ML-KEM-768 | 1.7631 h | 108.8 GB |
| X25519MLKEM768 | 4.2395 h | 112.0 GB |

The hybrid model therefore adds relatively little compute cost but much more transmitted cryptographic material.

## Combined operational cost

Using the current configured pricing:

### Azure

```text
Classical:       $0.41/month
ML-KEM-768:      $9.56/month
Hybrid:          $9.97/month
```

Hybrid incremental cost:

```text
$9.56/month
$114.72/year
```

### GCP

```text
Classical:       $0.35/month
ML-KEM-768:      $8.68/month
Hybrid:          $9.03/month
```

Hybrid incremental cost:

```text
$8.68/month
$104.19/year
```

The network component dominates these modeled totals.

## Signature operational model

For digital signatures, the company is assumed to perform the signing operation.

The model includes:

- signing CPU;
- signature bytes as outbound traffic.

Verification CPU is reported for context but excluded from company cost because verification is assumed to occur on the client side.

The model does not currently charge public-key or certificate-chain distribution once per signature.

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

The larger signature sizes are responsible for most of the modeled cost increase.

## Migration-cost scenarios

The repository also contains a configurable one-time migration model.

The central scenarios are:

| Scenario | Engineering hours | HSM upgrade | Total |
|---|---:|---:|---:|
| Startup | 192 h | $0 | $11,520 |
| Mid-size | 1,348 h | $15,000 | $116,100 |
| Enterprise | 9,400 h | $120,000 | $1,013,000 |

These values are hypothetical scenario assumptions.

They are not empirical estimates of what a real company will pay.

The model is intended to represent possible categories of migration effort such as:

- engineering implementation;
- testing;
- deployment work;
- infrastructure changes;
- HSM replacement or upgrades.

## Sensitivity analysis

Each migration scenario has low, central and high cases.

The committed sensitivity ranges are:

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

It should not be interpreted as a prediction of calendar migration duration.

## Limitations

The economic model intentionally simplifies real infrastructure.

It does not currently model:

- complete VM billing;
- autoscaling;
- TLS resumption;
- packet-level overhead;
- MTU fragmentation;
- full certificate-chain traffic;
- provider-specific enterprise discounts;
- reserved capacity;
- engineering dependencies;
- vendor delays;
- procurement delays;
- interoperability programs;
- staged production deployment.

Provider pricing tiers are also different from each other, so Azure and GCP outputs should not be interpreted as a controlled provider price comparison.

The useful result is the framework and the order of magnitude under explicit assumptions, not a universal cost forecast.