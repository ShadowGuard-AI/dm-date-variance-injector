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

    parser.add_argument("date", type=str, help="The date to modify (YYYY-MM-DD).")
    parser.add_argument(
        "-r",
        "--range",
        type=int,
        default=30,
        help="The range of days to vary the date by (default: 30).  A negative value allows dates in the past.",
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
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return date_obj
    except ValueError:
        raise ValueError(
            "Invalid date format. Please use YYYY-MM-DD (e.g., 2023-10-26)."
        )


def inject_date_variance(date_obj, range_days, max_range):
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

    if abs(range_days) > max_range:
        raise ValueError(
            f"The specified range ({range_days}) exceeds the maximum allowed range ({max_range})."
        )

    variance = random.randint(-abs(range_days), abs(range_days))  # Ensure both past and future dates are possible

    new_date = date_obj + datetime.timedelta(days=variance)
    return new_date


def main():
    """
    Main function to parse arguments, validate input, inject variance, and print the result.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Validate and parse the input date
        date_obj = validate_date(args.date)

        # Inject date variance
        modified_date = inject_date_variance(date_obj, args.range, args.max_range)

        # Format the output date
        formatted_date = modified_date.strftime(args.format)

        print(formatted_date)

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