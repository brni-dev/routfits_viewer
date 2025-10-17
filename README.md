# routfits_viewer
simple script for viewing roblox outfits

## Features

- Fetch all saved outfits for a Roblox user by their user ID.  
- Download all outfit thumbnails to a dedicated folder (`user_<USER_ID>/`).  
- Handles rate limits safely with delays.  
- Command line interface.

## Requirements

- Python 3.8+  
- [`requests`](https://pypi.org/project/requests/) library  

Install dependencies:

```bash
pip install requests
```

## Usage
```bash
python main.py <ROBLOX_USER_ID>
