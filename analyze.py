import subprocess
import pprint
import ast

data = [ ]
p = subprocess.Popen("cat results/*", shell=True, stdout=subprocess.PIPE)
data += [ r.strip()[:-4] for r in p.stdout ]

results = { }
overall = { }
for d in data:
    arch = next(f for f in d.split() if f.startswith('pkg=')).split('.')[-2].split('_')[-1]
    dict = ast.literal_eval(d.split('reasons=')[-1])
    results.setdefault(arch, {})
    for k,v in dict.items():
        results[arch].setdefault(k, 0)
        results[arch][k] += v
        overall.setdefault(k, 0)
        overall[k] += v

pprint.pprint(results)
pprint.pprint(overall)
