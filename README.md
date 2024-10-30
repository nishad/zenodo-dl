# Zenodo Downloader

`zenodo-dl.py` is a Python script that downloads files from a Zenodo record, verifies the file integrity using MD5 checksum, and organizes downloaded files based on their specified folder structure. It supports resuming interrupted downloads and skips files that already exist and pass the checksum verification.

## Features
- Downloads files from a specified Zenodo record.
- Organizes files into folder structures as per Zenodo metadata.
- Resumes interrupted downloads.
- Verifies downloaded files using MD5 checksum to ensure data integrity.

## Requirements
- Python 3.6 or higher
- `requests` and `tqdm` libraries

### Install Requirements
Install the dependencies by running:

```bash
pip install -r requirements.txt
```

### Usage

Run the script with a Zenodo record ID:

```bash
python zenodo-dl.py <record_id>
```

Replace <record_id> with the Zenodo record ID you want to download. For example:

```bash
python zenodo-dl.py 14010801
```

### Example Zenodo API URL

The script fetches file data using the Zenodo Deposition Files API, such as:

```
https://zenodo.org/api/deposit/depositions/14010801/files
```

### How It Works

1. Fetch File List: The script fetches file details from Zenodo’s API, including download URLs, filenames, and MD5 checksums.
2. Download with Resume Support: Files are downloaded, and partially downloaded files are resumed if interrupted.
3. Checksum Verification: After downloading, the file’s MD5 checksum is verified. Files with incorrect checksums are deleted and re-downloaded.

### Error Handling

* If a file fails the checksum check, it is removed and re-downloaded.
* If any download is interrupted, the script will resume downloading from where it left off.

### License

This project is licensed under the MIT License.

### Contribution

Feel free to open issues or submit pull requests for improvements and bug fixes.
