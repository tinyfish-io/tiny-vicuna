from os import path, makedirs, getcwd, chdir
from argparse import ArgumentParser
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)

p = ArgumentParser("Download LLaMA")
p.add_argument('--check-only', '-c', action='store_true', help="Only doing File")
p.add_argument('--dryrun', '-d', action='store_true', help="Dryrun, only print but no execute")
p.add_argument('--target', '-o', default='downloads', type=str, help="Target output diretory")
p.add_argument('--models', '-m', default=["7B","13B","30B","65B"], nargs='+', help="Models you want to download")
args = p.parse_args()

N_SHARD_DICT = {}
N_SHARD_DICT["7B"] = 0
N_SHARD_DICT["13B"] = 1
N_SHARD_DICT["30B"] = 3
N_SHARD_DICT["65B"] = 7

assert [m in ["7B","13B","30B","65B"] for m in args.models]
TARGET_FOLDER=lambda x: path.join(args.target, x)
PRESIGNED_URL=lambda x: f"https://dobf1k6cxlizq.cloudfront.net/{x}?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9kb2JmMWs2Y3hsaXpxLmNsb3VkZnJvbnQubmV0LyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2ODEzMTY1OTB9fX1dfQ__&Signature=LrCZnGTy9Kq3FPM8NBDAeh4b1gnEcsb5GdY51NcyIh3-UPCx-k5ZaanorXm7Itm8sDvo0MiVL-rxMcFE1q5fUwKDtGCH0VkgfVuLh9LmSC7ycTcw8clwm~S6aIb9LUPzPTkQi3SWiFG4n04aVivX5eSnEmfROZrLGt1K-xHIPJRq~0xMC6CbYX2Od8TNg8ONHLzAPGilZDEfx9mOzk1eFTgtA9jBLfs9Wzh26oh2oNyIc6MlwlCJzMAqC0GebrPC~mPbOBQmnNupDFSseuSZ~WE0d0SHGvNwg94dSkHKzYPqwaq2hssQVuhuZMuibx~0FuDpCLse~MRtzjihXB7PAw__&Key-Pair-Id=K231VYXPC1TA1R"

makedirs(TARGET_FOLDER(""), exist_ok=True)

models = ['tokenizer.model', "tokenizer_checklist.chk"]
for s in args.models:
    makedirs(TARGET_FOLDER(s), exist_ok=True)
    models.extend([f"{s}/consolidated.0{n}.pth" for n in range(N_SHARD_DICT[s]+1)])
    models.extend([f"{s}/{f}" for f in ["params.json", "checklist.chk"]])

for i, n in enumerate(models):
    logging.info(f"[{i}/{len(models)}]Downloding {n}...")
    wget_str = f"wget -c {PRESIGNED_URL(n)} -O {TARGET_FOLDER(n)}"
    if args.dryrun:
        logging.debug(f"-- {wget_str}")
    else:
        if not args.check_only:
            subprocess.run(wget_str.split(' '))


for i, s in enumerate(args.models):
    cmd = "md5sum -c checklist.chk"
    logging.info(f"[{i}/{len(args.models)}] Checking Model {s}...")
    if args.dryrun:
        logging.debug(f"-- {cmd}")
    else:
        subprocess.run(cmd.split(' '), cwd=TARGET_FOLDER(s))