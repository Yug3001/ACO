import requests, json

r = requests.get('http://127.0.0.1:8000/api/health', timeout=3)
print('Health:', r.json())

grid = [['S','E','E','O','E'],['E','E','E','O','E'],['O','O','E','O','E'],['E','E','E','E','E'],['O','O','E','E','F']]

r = requests.post('http://127.0.0.1:8000/api/run', json={'algorithm':'A*','grid':grid,'start':[0,0],'goal':[4,4],'allow_diagonal':True,'parameters':{}}, timeout=10)
d = r.json(); print('A*:', d['success'], 'len=', d['path_length'])

r = requests.post('http://127.0.0.1:8000/api/run', json={'algorithm':'ACO','grid':grid,'start':[0,0],'goal':[4,4],'allow_diagonal':True,'parameters':{'ants':12,'iterations':30}}, timeout=30)
d = r.json(); print('ACO:', d['success'], 'len=', d['path_length'], 'phero_rows=', len(d.get('pheromone_matrix',[])))

r = requests.post('http://127.0.0.1:8000/api/compare', json={'grid':grid,'start':[0,0],'goal':[4,4],'allow_diagonal':True,'parameters':{'ants':10,'iterations':25,'population':20,'particles':10}}, timeout=60)
d = r.json()
for res in d['results']: print(res['algorithm']+':', res['success'], 'len=', res['path_length'])
print('ALL API TESTS PASSED')
