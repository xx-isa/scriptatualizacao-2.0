import sys
from time import sleep

CAMINHO_SCRIPT = r"caminho/do/modulo/relatorios"
CAMINHO_CONFIG = r"caminho/do/arquivo/de/configuracao"

sys.path.insert(0, CAMINHO_SCRIPT)

print('rodando script com historico')
from relatorios import baixa_relatorios

baixa_relatorios(CAMINHO_CONFIG)

print('fim do script')
sleep(3)
