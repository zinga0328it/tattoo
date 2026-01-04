LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
CENTER, CORNERS, EDGES = 4, [0,2,6,8], [1,3,5,7]


def _norm(x): 
    return '0' if x in ('0',0) else ('1' if x in ('1',1) else ' ')


def _flat(board):
    if len(board)==3 and all(len(r)==3 for r in board):
        return [_norm(c) for r in board for c in r]
    if len(board)==9:
        return [_norm(c) for c in board]
    raise ValueError("board shape invalid")


def _two_and_gap(b, p):
    for a,b1,c in LINES:
        line=[b[a],b[b1],b[c]]
        if line.count(p)==2 and line.count(' ')==1:
            return [a,b1,c][line.index(' ')]
    return None


def _one_and_two_gaps(b, p):
    cand=[]
    for a,b1,c in LINES:
        line=[b[a],b[b1],b[c]]
        if line.count(p)==1 and line.count(' ')==2:
            idx=[a,b1,c]
            cand += [idx[i] for i,v in enumerate(line) if v==' ']
    for i in [CENTER]+CORNERS+EDGES:
        if i in cand: return i
    return None


def _fallback(b):
    if b[CENTER]==' ': return CENTER
    for i in CORNERS:
        if b[i]==' ': return i
    for i in EDGES:
        if b[i]==' ': return i
    return None


def mossa_macchina(board):
    b=_flat(board)
    m=_two_and_gap(b,'0') or _two_and_gap(b,'1') or _one_and_two_gaps(b,'0') or _fallback(b)
    return divmod(m,3) if m is not None else None


# test rapido
griglia = [['1','0','1'],
           [' ','0',' '],
           [' ',' ',' ']]
print(mossa_macchina(griglia))  # -> (2, 1)
