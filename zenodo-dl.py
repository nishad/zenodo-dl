import os
import sys
import hashlib
import requests
from tqdm import tqdm

def download_file(url, filepath, expected_checksum):
    # Check if partial file exists
    temp_filepath = f"{filepath}.part"
    resume_header = {}
    mode = 'wb'
    if os.path.exists(temp_filepath):
        # Resume download from where it left off
        existing_file_size = os.path.getsize(temp_filepath)
        resume_header = {'Range': f'bytes={existing_file_size}-'}
        mode = 'ab'  # Append mode for resuming

    # Make the request with resume headers if any
    with requests.get(url, headers=resume_header, stream=True) as response:
        response.raise_for_status()

        # Get the total size for the progress bar
        total_size = int(response.headers.get('content-length', 0)) + (os.path.getsize(temp_filepath) if mode == 'ab' else 0)

        with open(temp_filepath, mode) as file, tqdm(total=total_size, unit="B", unit_scale=True, desc=filepath) as progress_bar:
            # Update progress if resuming
            if mode == 'ab':
                progress_bar.update(os.path.getsize(temp_filepath))

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))

    # Verify checksum
    if verify_checksum(temp_filepath, expected_checksum):
        # Rename temp file to final filename after successful download and verification
        os.rename(temp_filepath, filepath)
        print(f"{filepath}: Download completed and checksum verified.")
        return True
    else:
        print(f"{filepath}: Checksum verification failed.")
        os.remove(temp_filepath)  # Remove the file if checksum fails
        return False

def verify_checksum(filepath, expected_checksum):
    """Calculates and verifies the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == expected_checksum

def main(record_id):
    # Create a main folder named after the record ID if it doesn't exist
    if not os.path.exists(record_id):
        os.makedirs(record_id)

    # Fetch list of files from Zenodo's Deposition Files API
    api_url = f"https://zenodo.org/api/deposit/depositions/{record_id}/files"
    response = requests.get(api_url)
    response.raise_for_status()
    files_data = response.json()

    # Download each file, check checksum, and save with folder structure if needed
    for file_info in files_data:
        filename = file_info['filename']
        file_url = file_info['links']['download']
        expected_checksum = file_info['checksum']

        # Determine full filepath and create necessary folders for nested structure
        filepath = os.path.join(record_id, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Skip download if file exists and checksum matches
        if os.path.exists(filepath):
            print(f"Checking existing file: {filename}")
            if verify_checksum(filepath, expected_checksum):
                print(f"{filename}: File already exists and checksum is verified. Skipping download.")
                continue
            else:
                print(f"{filename}: File exists but checksum does not match. Resuming download...")

        # Download the file with resume support
        success = download_file(file_url, filepath, expected_checksum)
        if not success:
            print(f"{filename}: Download failed or checksum verification failed.")
            continue

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_zenodo.py <record_id>")
        sys.exit(1)

    record_id = sys.argv[1]
    main(record_id)
