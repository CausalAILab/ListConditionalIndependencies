from typing import List


class AlgorithmType():

    id_: str
    name: str
    params: List[str]

    def __init__(self, id_, name, params):
        self.id_ = id_
        self.name = name
        self.params = params

algListGMP = AlgorithmType('listgmp', 'ListGMP', ['n', 'm', 'md', 'mb', 'CI', 'runtime'])
algListCIBF = AlgorithmType('listcibf', 'ListCIBF', ['n', 'm', 'md', 'mb', 'CI', 'runtime', 's', 'S', 'Splus'])
algListCI = AlgorithmType('listci', 'ListCI', ['n', 'm', 'md', 'mb', 'CI', 'runtime', 's'])

algMap = dict()
algMap[algListGMP.id_] = algListGMP
algMap[algListCIBF.id_] = algListCIBF
algMap[algListCI.id_] = algListCI