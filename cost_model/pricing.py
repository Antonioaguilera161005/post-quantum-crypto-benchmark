from pathlib import Path

import pandas as pd


PRICING_FILE = Path(
    "cost_model/config/cloud_pricing.csv"
)


REQUIRED_COLUMNS = {
    "provider",
    "service",
    "region",
    "product",
    "price",
    "currency",
    "billing_unit",
    "free_units_month",
    "vcpus",
    "source_name",
    "source_type",
    "checked_date",
}


def load_cloud_pricing():
    if not PRICING_FILE.exists():
        raise FileNotFoundError(
            f"Missing pricing configuration: "
            f"{PRICING_FILE}"
        )

    pricing = pd.read_csv(
        PRICING_FILE
    )

    missing = (
        REQUIRED_COLUMNS
        - set(pricing.columns)
    )

    if missing:
        raise RuntimeError(
            "Missing cloud-pricing columns: "
            f"{sorted(missing)}"
        )

    return pricing


def get_service_pricing(service):
    pricing = load_cloud_pricing()

    rows = pricing[
        pricing["service"] == service
    ].copy()

    if rows.empty:
        raise RuntimeError(
            f"No pricing rows found for "
            f"service={service}"
        )

    return rows


def get_provider_pricing(
    provider,
    service,
):
    pricing = load_cloud_pricing()

    rows = pricing[
        (
            pricing["provider"]
            == provider
        )
        &
        (
            pricing["service"]
            == service
        )
    ]

    if len(rows) != 1:
        raise RuntimeError(
            "Expected exactly one pricing row "
            f"for {provider}/{service}; "
            f"found {len(rows)}."
        )

    return rows.iloc[0]


def decimal_gb_to_gib(decimal_gb):
    bytes_per_gb = 1_000_000_000
    bytes_per_gib = 1024 ** 3

    total_bytes = (
        decimal_gb
        * bytes_per_gb
    )

    return (
        total_bytes
        / bytes_per_gib
    )


def convert_network_units(
    decimal_gb,
    billing_unit,
):
    if billing_unit == "GB":
        return decimal_gb

    if billing_unit == "GiB":
        return decimal_gb_to_gib(
            decimal_gb
        )

    raise ValueError(
        "Unsupported network billing unit: "
        f"{billing_unit}"
    )