import tomllib

# Bump in lockstep with the writer in PyDotBot's
# dotbot/calibration/lighthouse2.py (CALIBRATION_SCHEMA_VERSION). The
# .toml's [calibration].data_hex carries the same byte payload as the
# legacy calibration.out, so swarmit only needs to unwrap it.
CALIBRATION_SCHEMA_VERSION = 1


def load_toml_config(path):
    if not path:
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def read_lh2_calibration_payload(path):
    """Return the raw LH2 calibration byte payload from `path`.

    Accepts either the legacy raw binary (1-byte count + N×36B int32 LE
    matrices, e.g. calibration.out) or a calibration-*.toml written by
    `dotbot calibrate-lh2` (schema with [calibration].data_hex). Format is
    chosen by file extension. Malformed TOML raises ValueError so the CLI
    can report it cleanly rather than passing garbage to the controller.
    """
    if str(path).lower().endswith(".toml"):
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(f"{path}: invalid TOML ({exc})") from exc
        schema = data.get("schema_version", 0)
        if schema != CALIBRATION_SCHEMA_VERSION:
            raise ValueError(
                f"{path}: unsupported calibration schema_version {schema} "
                f"(this build supports {CALIBRATION_SCHEMA_VERSION})"
            )
        try:
            hex_data = data["calibration"]["data_hex"]
        except (KeyError, TypeError) as exc:
            raise ValueError(
                f"{path}: missing [calibration].data_hex"
            ) from exc
        try:
            return bytes.fromhex(hex_data)
        except ValueError as exc:
            raise ValueError(
                f"{path}: [calibration].data_hex is not valid hex ({exc})"
            ) from exc
    with open(path, "rb") as f:
        return f.read()
