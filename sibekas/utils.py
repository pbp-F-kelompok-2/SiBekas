"""Shared utility functions for the SiBekas project."""


def format_rupiah(value):
    """Format an integer value as Indonesian Rupiah string.

    Example:
        >>> format_rupiah(150000)
        'Rp 150.000'
    """
    return f"Rp {value:,}".replace(",", ".")
