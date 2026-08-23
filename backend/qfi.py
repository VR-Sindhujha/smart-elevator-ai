def calculate_qfi(skipped_count, threshold=5):
    """
    Calculate Queue Fairness Index (QFI).

    More repeated skips -> higher fairness priority.

    QFI ranges from 0 to 1.
    """

    if skipped_count <= 0:
        return 0.0

    qfi = skipped_count / threshold

    return round(min(qfi, 1.0), 2)


# ---------------------------------------------------------
# QFI DEMONSTRATION
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("              QUEUE FAIRNESS INDEX (QFI)")
    print("=" * 60)

    threshold = 5

    print()
    print("Floor 7 Request")
    print("-" * 60)

    for skipped in range(0, 6):

        qfi = calculate_qfi(skipped, threshold)

        print(
            f"Skipped {skipped} time(s)"
            f"  →  QFI = {qfi:.2f}"
        )

    print()
    print("Interpretation")
    print("-" * 60)

    print("Repeated skipping")
    print("       ↓")
    print("QFI increases")
    print("       ↓")
    print("Fairness threshold reached")
    print("       ↓")
    print("FAIRNESS OVERRIDE")
    print("       ↓")
    print("SERVE REQUEST")

    print()
    print("=" * 60)