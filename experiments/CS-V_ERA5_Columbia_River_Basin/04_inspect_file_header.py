import sys
import os

def main():
    file_path = os.path.join("data", "era5_jan1980_hourly.nc")
    print(f"Inspecting file header for '{file_path}'")

    try:
        with open(file_path, "rb") as f:
            # Read first 8 bytes
            header = f.read(8)
            hex_values = " ".join(f"{byte:02x}" for byte in header)
            print("First 8 bytes (hex):", hex_values)

            # Check gzip signature
            if len(header) >= 2 and header[0] == 0x1f and header[1] == 0x8b:
                print("Signature match: File is gzip-compressed (0x1f 0x8b).")
            else:
                print("No gzip signature found: File is NOT gzip-compressed.")

            # Read next 256 bytes for text snippet
            snippet_bytes = f.read(256)
            snippet_text = snippet_bytes.decode("utf-8", errors="ignore")
            print("\nNext 256 bytes decoded as UTF-8 (snippet):")
            print(snippet_text)

    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()