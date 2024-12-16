from .RelatoriosSemHistorico import baixa_sem_historico
from .Relatorios import baixa_relatorios

__all__ = ["baixa_relatorios", "baixa_sem_historico"]

usage = """
Importe uma das funções do código e chame com o caminho do arquivo de configuração
"""

def __main__():
    print(usage)
