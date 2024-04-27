from src.inference.utils.graph_utils import compareNames

from src.inference.utils.graph_utils import GraphUtils as gu
from src.inference.utils.set_utils import SetUtils as su
from src.common.object_utils import ObjectUtils as ou


def TestSep(G, X, Y, Z=[]):
    X = ou.makeArray(X)
    Y = ou.makeArray(Y)
    Z = ou.makeArray(Z)

    # Bayes Ball
    # https://github.com/lingxuez/bayes-net/blob/9ba18d08f85d04b566c6a103be67242eab8dc95a/src/BN.py#L114
    AnZ = gu.ancestors(Z, G)

    Q = []

    for x in X:
        Q.append((x['name'], 'up'))

    visited = set()

    while len(Q) > 0:
        (name, dir) = Q.pop()
        node = gu.getNodeByName(name, G)

        if (name, dir) not in visited:
            visited.add((name, dir))

            if not su.belongs(node, Z, compareNames) and su.belongs(node, Y, compareNames):
                return False

            if dir == 'up' and not su.belongs(node, Z, compareNames):
                for parent in G.parents(node):
                    Q.append((parent['name'], 'up'))

                for child in G.children(node):
                    Q.append((child['name'], 'down'))

            elif dir == 'down':
                if not su.belongs(node, Z, compareNames):
                    for child in G.children(node):
                        Q.append((child['name'], 'down'))

                if su.belongs(node, Z, compareNames) or su.belongs(node, AnZ, compareNames):
                    for parent in G.parents(node):
                        Q.append((parent['name'], 'up'))

    return True

def writeNodeNames(nodes):
    return ', '.join(nodes) if len(nodes) > 0 else '\emptyset'

def nodeNamesToString(nodes, sortByName = True):
    names = list(map(lambda n: n['name'] if n is not None and 'name' in n else '\emptyset', nodes))

    if sortByName:
        names = sorted(names)

    return writeNodeNames(names)
