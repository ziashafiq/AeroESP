import os
import sys


REQUIRED = [
    "DJANGO_SECRET_KEY",
    "AEROESP_SECRET_KEY",
    "AEROESP_DB_NAME",
    "AEROESP_DB_USER",
    "AEROESP_DB_PASSWORD",
    "AEROESP_DB_HOST",
]


def main():

    missing = [
        name
        for name in REQUIRED
        if not os.getenv(name)
    ]

    if missing:

        print(
            "PRODUCTION CHECK: FAILED"
        )

        for name in missing:
            print(
                f"MISSING: {name}"
            )

        sys.exit(1)

    print(
        "PRODUCTION CHECK: OK"
    )


if __name__ == "__main__":
    main()