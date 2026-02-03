"""Interactive script to submit PDF parsing tasks."""

import os
import sys
import httpx

# Configuration
API_URL = "http://localhost:8000/api/tasks"
FILE_DIR = os.path.join(os.path.dirname(__file__), "file")


def get_pdf_files():
    """Get list of PDF files in the file directory."""
    if not os.path.exists(FILE_DIR):
        print(f"Error: Directory '{FILE_DIR}' does not exist")
        return []

    files = [f for f in os.listdir(FILE_DIR) if f.lower().endswith('.pdf')]
    return files


def select_file(files):
    """Interactive file selection."""
    print("\n=== PDF Files ===")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    print(f"  0. Exit")

    while True:
        try:
            choice = input("\nSelect file number: ").strip()
            if choice == '0':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]
            print("Invalid selection, please try again")
        except ValueError:
            print("Please enter a number")


def submit_task(file_path):
    """Submit a task to the API."""
    payload = {
        "async": False,  # Sync mode
        "priority": 5,
        "payload": {
            "file": file_path,
            # Add other MinerU parameters as needed
        }
    }

    print(f"\nSubmitting task...")
    print(f"  File: {file_path}")
    print(f"  Mode: Sync (blocking)")

    try:
        with httpx.Client(timeout=600) as client:  # 10 min timeout for large PDFs
            response = client.post(API_URL, json=payload)
            response.raise_for_status()
            result = response.json()

            print(f"\n=== Result ===")
            print(f"  Task ID: {result.get('task_id')}")
            print(f"  Status: {result.get('status')}")

            if result.get('error'):
                print(f"  Error: {result.get('error')}")

            if result.get('result'):
                print(f"  Result: {result.get('result')}")

            return result

    except httpx.ConnectError:
        print(f"\nError: Cannot connect to {API_URL}")
        print("Make sure MinerU Center is running (uv run python run.py)")
    except httpx.HTTPStatusError as e:
        print(f"\nHTTP Error: {e.response.status_code}")
        print(f"  Detail: {e.response.text}")
    except Exception as e:
        print(f"\nError: {e}")

    return None


def main():
    print("=== MinerU Center Task Submitter ===")

    files = get_pdf_files()
    if not files:
        print("No PDF files found in 'file' directory")
        sys.exit(1)

    while True:
        selected = select_file(files)
        if selected is None:
            print("Bye!")
            break

        file_path = os.path.join(FILE_DIR, selected)
        submit_task(file_path)

        print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
