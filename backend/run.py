"""Single-command launcher.

Runs Alembic migrations against Supabase PostgreSQL and then starts one FastAPI/Uvicorn
process. The FastAPI lifespan starts the scheduler and configured logical workers in
that same process.
"""

import uvicorn
import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run with auto-reload enabled",
    )
    args = parser.parse_args()

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
    )

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=args.dev,
    )


if __name__ == "__main__":
    main()