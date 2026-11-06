"""Geometric shim sizing for a pad with measured working heights, mm."""
def shim_interval(gap_low, gap_high, working_low, working_high, shim_error):
    if not (0 <= gap_low <= gap_high and 0 < working_low <= working_high and shim_error >= 0):
        raise ValueError("Niepoprawny przedział wymiarów")
    # For every combination: working_low <= gap - actual shim <= working_high.
    lower = max(0., gap_high - working_high + shim_error)
    upper = gap_low - working_low - shim_error
    return (lower, upper) if lower <= upper else None
