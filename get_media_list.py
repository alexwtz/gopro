# communicate_via_cohn.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed Mar 27 22:05:49 UTC 2024

import sys
import json
import argparse
import asyncio
from base64 import b64encode
from pathlib import Path
import os

import requests

from tutorial_modules import logger

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

async def main(ip_address: str, username: str, password: str, certificate: Path) -> None:
    url = f"https://{ip_address}" + "/gopro/media/list"
    logger.debug(f"Sending:  {url}")

    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    response = requests.get(
        url,
        timeout=10,
        headers={"Authorization": f"Basic {token}"},
        verify=str(certificate),
    )
    # Check for errors (if an error is found, an exception will be raised)
    response.raise_for_status()
    logger.info("Command sent successfully")
    # Log response as json
    resp=response.json()
    #logger.info(f"Response: {json.dumps(resp, indent=4)}")
    #http://10.5.5.9:8080/videos/DCIM/{directory}/{filename}
    for d in resp["media"]:
        for f in d["fs"]:
            print(f)
            download = False
            if os.path.isfile(f["n"]):
                if (int)(os.path.getsize(f["n"])) == (int)(f['s']):
                    print(f'can safely remove file {f["n"]}')
                    res = requests.get(
                        f"https://{ip_address}/gopro/media/delete/file?path={d['d']}/{f['n']}",
                        timeout=10,
                        headers={"Authorization": f"Basic {token}"},
                        verify=str(certificate),
                    )
                    print(res)
                else:
                    download = True
            if download:
                with requests.get(
                    f"https://{ip_address}/videos/DCIM/{d['d']}/{f['n']}",
                    timeout=10,
                    headers={"Authorization": f"Basic {token}"},
                    verify=str(certificate),
                ) as r:
                    r.raise_for_status()
                    with open(f['n'], 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192): 
                            # If you have chunk encoded response uncomment if
                            # and set chunk_size parameter to None.
                            #if chunk: 
                            f.write(chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demonstrate HTTPS communication via COHN.")
    parser.add_argument("ip_address", type=str, help="IP Address of camera on the home network")
    parser.add_argument("username", type=str, help="COHN username")
    parser.add_argument("password", type=str, help="COHN password")
    parser.add_argument("certificate", type=Path, help="Path to read COHN cert from.", default=Path("cohn.crt"))
    args = parser.parse_args()

    try:
        asyncio.run(main(args.ip_address, args.username, args.password, args.certificate))
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)
        sys.exit(-1)
    else:
        sys.exit(0)
