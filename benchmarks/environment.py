import json
import os
import platform
import re
import shutil
import subprocess
import sys

from datetime import datetime, timezone
from pathlib import Path

import cryptography
import oqs

from cryptography.hazmat.backends.openssl.backend import (
    backend,
)


NATIVE_OUTPUT_DIR = Path(
    "results/native"
)

NATIVE_DURATION_SECONDS = 3


def command_output(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
    ):
        return None


def get_cpu_model():

    # ========================================================
    # WINDOWS
    # ========================================================

    if os.name == "nt":

        result = command_output(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                (
                    "(Get-CimInstance Win32_Processor "
                    "| Select-Object -First 1 "
                    "-ExpandProperty Name)"
                ),
            ]
        )

        if result:
            return result.strip()

    # ========================================================
    # LINUX
    # ========================================================

    if sys.platform.startswith("linux"):

        cpuinfo = Path(
            "/proc/cpuinfo"
        )

        if cpuinfo.exists():

            for line in (
                cpuinfo.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).splitlines()
            ):

                if line.lower().startswith(
                    "model name"
                ):

                    return (
                        line.split(
                            ":",
                            1,
                        )[1]
                        .strip()
                    )

    # ========================================================
    # MACOS
    # ========================================================

    if sys.platform == "darwin":

        result = command_output(
            [
                "sysctl",
                "-n",
                "machdep.cpu.brand_string",
            ]
        )

        if result:
            return result.strip()

    return (
        platform.processor()
        or "unknown"
    )


def get_windows_power_scheme():

    if os.name != "nt":
        return None

    result = command_output(
        [
            "powercfg",
            "/getactivescheme",
        ]
    )

    return result


def get_git_metadata():

    commit = command_output(
        [
            "git",
            "rev-parse",
            "HEAD",
        ]
    )

    status = command_output(
        [
            "git",
            "status",
            "--porcelain",
        ]
    )

    return {
        "commit": commit,
        "dirty": bool(status),
    }

def get_campaign_metadata():

    inherited_started_at = os.environ.get(
        "PQC_CAMPAIGN_STARTED_AT_UTC"
    )

    inherited_commit = os.environ.get(
        "PQC_CAMPAIGN_GIT_COMMIT"
    )

    inherited_dirty = os.environ.get(
        "PQC_CAMPAIGN_GIT_DIRTY"
    )

    if (
        inherited_started_at
        and inherited_commit
        and inherited_dirty is not None
    ):
        return {
            "started_at_utc":
                inherited_started_at,

            "commit":
                inherited_commit,

            "dirty":
                inherited_dirty.lower()
                == "true",
        }

    git = get_git_metadata()

    return {
        "started_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "commit":
            git["commit"],

        "dirty":
            git["dirty"],
    }

def find_native_binary(
    binary_name,
):

    executable_name = (
        f"{binary_name}.exe"
        if os.name == "nt"
        else binary_name
    )

    candidates = []

    configured_build_dir = (
        os.environ.get(
            "LIBOQS_BUILD_DIR"
        )
    )

    if configured_build_dir:

        build_dir = Path(
            configured_build_dir
        )

        candidates.extend(
            [
                build_dir
                / "tests"
                / executable_name,

                build_dir
                / "tests"
                / "Release"
                / executable_name,
            ]
        )

    candidates.extend(
        [
            Path.home()
            / "liboqs-release"
            / "build"
            / "tests"
            / executable_name,

            Path.home()
            / "liboqs-release"
            / "build"
            / "tests"
            / "Release"
            / executable_name,

            Path.home()
            / "liboqs"
            / "build"
            / "tests"
            / executable_name,

            Path.home()
            / "liboqs"
            / "build"
            / "tests"
            / "Release"
            / executable_name,
        ]
    )

    for candidate in candidates:

        if candidate.exists():
            return candidate

    system_binary = shutil.which(
        executable_name
    )

    if system_binary:
        return Path(
            system_binary
        )

    raise FileNotFoundError(
        f"Could not find native "
        f"{executable_name}. "
        "Set LIBOQS_BUILD_DIR to the "
        "liboqs build directory."
    )


def parse_configuration(
    output,
):

    fields = {}

    mapping = {
        "Target platform":
            "target_platform",

        "Compiler":
            "compiler",

        "Compile options":
            "compile_options",

        "OQS version":
            "oqs_version",

        "OpenSSL enabled":
            "openssl_enabled",

        "AES":
            "aes_implementation",

        "SHA-2":
            "sha2_implementation",

        "SHA-3":
            "sha3_implementation",

        "OQS build flags":
            "oqs_build_flags",

        "CPU exts active":
            "cpu_extensions_active",
    }

    for line in output.splitlines():

        for source, target in (
            mapping.items()
        ):

            if line.startswith(
                source
            ):

                value = (
                    line.split(
                        ":",
                        1,
                    )[1]
                    .strip()
                )

                fields[target] = value

    flags = fields.get(
        "oqs_build_flags",
        "",
    )

    build_match = re.search(
        r"CMAKE_BUILD_TYPE=([^\s]+)",
        flags,
    )

    fields[
        "build_configuration"
    ] = (
        build_match.group(1)
        if build_match
        else None
    )

    fields[
        "oqs_dist_build"
    ] = (
        "OQS_DIST_BUILD"
        in flags.split()
    )

    extensions = fields.get(
        "cpu_extensions_active",
        "",
    )

    fields[
        "cpu_extensions"
    ] = (
        extensions.split()
        if extensions
        else []
    )

    return fields


def parse_operation_means(
    output,
    operations,
):

    means = {}

    for operation in operations:

        pattern = (
            rf"^\s*{re.escape(operation)}"
            r"\s*\|\s*"
            r"(\d+)"
            r"\s*\|\s*"
            r"([0-9.]+)"
            r"\s*\|\s*"
            r"([0-9.]+)"
        )

        match = re.search(
            pattern,
            output,
            flags=re.MULTILINE,
        )

        if match:

            means[operation] = {
                "iterations":
                    int(
                        match.group(1)
                    ),

                "total_time_seconds":
                    float(
                        match.group(2)
                    ),

                "mean_microseconds":
                    float(
                        match.group(3)
                    ),
            }

    return means


def run_native_crosscheck(
    benchmark_type,
):

    NATIVE_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if benchmark_type == "kem":

        binary = find_native_binary(
            "speed_kem"
        )

        algorithm = "ML-KEM-768"

        operations = [
            "keygen",
            "encaps",
            "decaps",
        ]

        output_file = (
            NATIVE_OUTPUT_DIR
            / "ml_kem_768_speed.txt"
        )

    elif benchmark_type == "signature":

        binary = find_native_binary(
            "speed_sig"
        )

        algorithm = "ML-DSA-44"

        operations = [
            "keypair",
            "sign",
            "verify",
        ]

        output_file = (
            NATIVE_OUTPUT_DIR
            / "ml_dsa_44_speed.txt"
        )

    else:
        raise ValueError(
            "benchmark_type must be "
            "'kem' or 'signature'"
        )

    command = [
        str(binary),
        "-d",
        str(
            NATIVE_DURATION_SECONDS
        ),
        algorithm,
    ]

    print()
    print("=" * 80)
    print(
        f" NATIVE CROSS-CHECK: "
        f"{algorithm}"
    )
    print("=" * 80)

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    output = (
        result.stdout
        + result.stderr
    )

    output_file.write_text(
        output,
        encoding="utf-8",
    )

    configuration = (
        parse_configuration(
            output
        )
    )

    operation_means = (
        parse_operation_means(
            output,
            operations,
        )
    )

    print(
        f"Native output saved to: "
        f"{output_file}"
    )

    return {
        "algorithm":
            algorithm,

        "binary":
            str(binary.resolve()),

        "duration_seconds_per_operation":
            NATIVE_DURATION_SECONDS,

        "raw_output_file":
            str(output_file),

        "configuration":
            configuration,

        "operation_means":
            operation_means,
    }


def save_run_environment(
    run_dir,
    run_id,
    suite_name,
    native_crosscheck,
    campaign_metadata,
    warmup_iterations,
    benchmark_iterations,
):

    output_path = (
        run_dir
        / "environment.json"
    )

    existing = {}

    if output_path.exists():

        try:

            existing = json.loads(
                output_path.read_text(
                    encoding="utf-8"
                )
            )

        except json.JSONDecodeError:
            existing = {}

    configuration = (
        native_crosscheck.get(
            "configuration",
            {},
        )
    )

    environment = {
        "run_id":
            run_id,

        "cpu_model":
            get_cpu_model(),

        "processor":
            platform.processor(),

        "platform":
            platform.platform(),

        "machine":
            platform.machine(),

        "python_version":
            sys.version,

        "python_executable":
            sys.executable,

        "cryptography_version":
            cryptography.__version__,

        "openssl_version":
            backend.openssl_version_text(),

        "liboqs_version":
            oqs.oqs_version(),

        "liboqs_python_version":
            oqs.oqs_python_version(),

        "liboqs_library_path":
            str(
                oqs.native()._name
            ),

        "oqs_install_path":
            os.environ.get(
                "OQS_INSTALL_PATH"
            ),

        "build_configuration":
            configuration.get(
                "build_configuration"
            ),

        "oqs_dist_build":
            configuration.get(
                "oqs_dist_build"
            ),

        "oqs_build_flags":
            configuration.get(
                "oqs_build_flags"
            ),

        "cpu_extensions":
            configuration.get(
                "cpu_extensions",
                [],
            ),

        "compiler":
            configuration.get(
                "compiler"
            ),

        "target_platform":
            configuration.get(
                "target_platform"
            ),


        "windows_power_scheme":
            get_windows_power_scheme(),

        "warmup_iterations":
            warmup_iterations,

        "benchmark_iterations":
            benchmark_iterations,
    }

    # Preserve information generated by another suite.
    suite_records = existing.get(
        "suite_records",
        {},
    )

    suite_records[
    suite_name
] = {
    "campaign_started_at_utc":
        campaign_metadata[
            "started_at_utc"
        ],

    "git_commit":
        campaign_metadata[
            "commit"
        ],

    "git_dirty_at_campaign_start":
        campaign_metadata[
            "dirty"
        ],

    "recorded_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "native_crosscheck":
        native_crosscheck,
}

    environment[
        "suite_records"
    ] = suite_records

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            environment,
            file,
            indent=4,
        )

    print(
        f"Environment saved to: "
        f"{output_path}"
    )