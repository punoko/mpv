#!/usr/bin/env python3
import fileinput
import shutil
import subprocess
import sys
from pathlib import Path


def get_binary(name: str = "mpv"):
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = shutil.which(name)
        if path is None:
            raise FileNotFoundError(f"'{name}' not found in PATH")
    return Path(path).resolve(strict=True)


def get_version(binary: Path):
    r = subprocess.run(
        [binary, "--version"],
        capture_output=True,
        check=True,
        text=True,
    )
    return r.stdout.splitlines()[0].split()[1]


def bundle_init(bundle: Path):
    if bundle.is_dir():
        shutil.rmtree(bundle)
    shutil.copytree("skeleton", bundle)


def patch_plist(bundle, version, category: str = "video"):
    plist = bundle / "Contents" / "Info.plist"
    for line in fileinput.input(plist, inplace=True):
        print(line.rstrip().replace("${VERSION}", version).replace("${CATEGORY}", category))


def codesign(path: Path) -> None:
    subprocess.run(["codesign", "--force", "-s", "-", path])


def main():
    source = get_binary()
    version = get_version(source)
    bundle = Path("mpv.app")
    binary = bundle / "Contents" / "MacOS" / "mpv"

    print(f"Creating macOS application bundle (version: {version})...")

    print("> copying bundle skeleton")
    bundle_init(bundle)

    print(f"> copying binary {source}")
    binary.parent.mkdir(exist_ok=True)
    shutil.copy(source, binary)

    print("> generating Info.plist")
    patch_plist(bundle, version)

    print("> signing bundle with ad-hoc pseudo identity")
    for path in (binary, bundle):
        codesign(path)

    print("Done.")


if __name__ == "__main__":
    main()
