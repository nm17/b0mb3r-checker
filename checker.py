import asyncio
import os
import sys
import time
from glob import glob
from pathlib import Path
import subprocess

import pandas as pd

to_remove = {'Service', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', "random", "string", "randint"}

subprocess.run(["pip", "install", "-r", "b0mb3r/requirements.txt"], env=os.environ)

sys.path.extend([str(Path.cwd()), str(Path.cwd().joinpath("b0mb3r"))])

services_name = map(lambda a: Path(a).name.replace(".py", ""), glob("b0mb3r/b0mb3r/services/*.py"))

print("При тесте будут всплывать ошибки, игнорьте их.")

phone = input("Ноиер телефона без кода страны и плюсов> ")
country_code = int(input("Код страны (Например 375, без плюсов)> "))

df = pd.DataFrame()


async def run():
    global df
    for service in services_name:
        t1 = time.time()
        try:
            module = getattr(__import__("b0mb3r.services." + service).services, service)
            cls = set(dir(module)).difference(to_remove).pop()
            cls = getattr(module, cls)
            serv = cls(phone, country_code)
        except:
            print(service, "crashed")
            df = df.append({"name": service, "recived": -1, "time_passed": t1 - time.time()}, ignore_index=True)
            continue
        if country_code not in cls.phone_codes:
            print("skipping service", service)
            continue
        try:
            await serv.run()
        except:
            print(service, "crashed")
            df = df.append({"name": service, "recived": -1, "time_passed": t1 - time.time()}, ignore_index=True)
            continue
        recived = input("Вы получили сообщение? (напишите y на англ если пришло, иначе оставьте пустым)> ").strip() == "y"
        df = df.append({"name": service, "recived": int(recived), "time_passed": t1 - time.time()}, ignore_index=True)

    df.to_csv(f"out_{country_code}.csv")

asyncio.run(run())