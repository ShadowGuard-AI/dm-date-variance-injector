import argparse
import logging
import random
import datetime
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(
        description="Introduces a random variance within a specified range to date values, "
                    "preserving temporal relationships while obscuring exact dates."
    )

    parser.add_argument("date", type=str, nargs="+", help="One or more dates to modify (YYYY-MM-DD). All dates in one run share a single drawn offset, so their order is preserved.")
    parser.add_argument(
        "-r",
        "--range",
        type=int,
        default=30,
        help="The range of days to vary the date by (default: 30). A positive value draws only into the future, from 1 to the range. A negative value draws only into the past, from the range to -1.",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Optional seed for the shared offset draw, so a run can be reproduced.",
    )
    parser.add_argument(
        "-m",
        "--max-range",
        type=int,
        default=365,
        help="The maximum range of days to vary the date by. Prevent excessively large variance. (default: 365).",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="%Y-%m-%d",
        help="The output date format (default: %%Y-%%m-%%d). See datetime.strftime() for format codes.",
    )

    return parser


def validate_date(date_str):
    """
    Validates that the input date string is in the correct format (YYYY-MM-DD).

    Args:
        date_str (str): The date string to validate.

    Returns:
        datetime.date: The validated date object.

    Raises:
        ValueError: If the date string is not in the correct format.
    """
    try:
        # The input format is fixed here on purpose: the --format option is
        # output only, whatever a caller expects it to mean. strptime is
        # also more forgiving than the error text below: a date like
        # 2023-1-5 parses fine even though it is not zero padded.
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return date_obj
    except ValueError:
        raise ValueError(
            "Invalid date format. Please use YYYY-MM-DD (e.g., 2023-10-26)."
        )


def inject_date_variance(date_obj, range_days, max_range, offset=None):
    """
    Injects a random variance within the specified range to a date.

    Args:
        date_obj (datetime.date): The date object to modify.
        range_days (int): The range of days to vary the date by.
        max_range (int): The maximum allowed range for variance.

    Returns:
        datetime.date: The modified date object.

    Raises:
        ValueError: If the range_days exceeds max_range in absolute value.
    """

    if max_range < 0:
        raise ValueError("The maximum range cannot be negative.")

    if abs(range_days) > max_range:
        raise ValueError(
            f"The specified range ({range_days}) exceeds the maximum allowed range ({max_range})."
        )

    # When main supplies the shared offset, the two range checks above run
    # a second time for nothing: draw_variance already enforced them, and
    # max_range plays no part in applying an offset that already exists.
    # The duplication keeps this function safe to call on its own, which is
    # the only reason I leave it standing.
    variance = offset if offset is not None else draw_variance(range_days, max_range)

    new_date = date_obj + datetime.timedelta(days=variance)
    return new_date


def draw_variance(range_days, max_range):
    """Draw one offset. A positive range draws only into the future and a
    negative range only into the past. Zero range draws zero."""
    if max_range < 0:
        raise ValueError("The maximum range cannot be negative.")
    if abs(range_days) > max_range:
        raise ValueError(
            f"The specified range ({range_days}) exceeds the maximum allowed range ({max_range})."
        )
    if range_days > 0:
        return random.randint(1, range_days)
    if range_days < 0:
        return random.randint(range_days, -1)
    return 0


def main():
    """
    Main function to parse arguments, validate input, inject variance, and print the result.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        if args.seed is not None:
            random.seed(args.seed)
        # One shared offset for every date in this run, so the order of the
        # dates is the order of the originals. With a seed, this shared
        # offset is the seeded draw.
        # A shared offset preserves more than order: the gaps between the
        # dates come out exactly as they went in, because every date moves
        # by the same number of days. Anyone who knows one true date in the
        # run can work the offset out and recover all of them, which is the
        # price of keeping the gaps, and worth stating where the draw happens.
        # The draw also happens before any date is validated, and the loop
        # prints as it goes: a bad date halfway through leaves the earlier
        # shifted dates already printed before the run exits 1.
        shared_offset = draw_variance(args.range, args.max_range)
        for date_str in args.date:
            date_obj = validate_date(date_str)
            modified_date = inject_date_variance(date_obj, args.range, args.max_range, offset=shared_offset)
            print(modified_date.strftime(args.format))

    except ValueError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Usage Examples:
    # 1. Basic usage: python main.py 2023-10-26
    # 2. Specify a different range: python main.py 2023-10-26 -r 10
    # 3. Specify a custom date format: python main.py 2023-10-26 -f "%m/%d/%Y"
    # 4. Specify a maximum range limit: python main.py 2023-10-26 -r 50 -m 100
    # 5. Check error handling: python main.py 2023/10/26 (invalid date format)
    main()