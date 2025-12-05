# updater.py
import requests
import os

HOSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'hosts')
ADLISTS = [
    # añade URLs de hosts/adlists; ejemplo:
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    # puedes añadir más
]

def download_list(url, outpath):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(r.text)
        return True
    except Exception as e:
        print("Error downloading", url, e)
        return False

def update_all():
    os.makedirs(HOSTS_DIR, exist_ok=True)
    for i, url in enumerate(ADLISTS):
        fname = f'adlist_{i}.txt'
        outpath = os.path.join(HOSTS_DIR, fname)
        print("Downloading", url)
        download_list(url, outpath)
    print("Update done.")

if __name__ == '__main__':
    update_all()
