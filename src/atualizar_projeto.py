from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.auditar_dados import auditar_dados
from src.calcular_indice_risco import gerar_indices
from src.carregar_dados import resolver_anos_analise
from src.limpar_dados import gerar_tratados
from src.modelar_dados import gerar_modelados
from src.verificar_dados_publicos import (
    ResultadoVerificacao,
    imprimir_relatorio,
    verificar_arquivos_brutos,
    verificar_dados_publicos,
    verificar_documentacao_fonte,
    verificar_fonte_publica_online,
)


def imprimir_etapa(titulo: str) -> None:
    print()
    print("=" * 80)
    print(titulo)
    print("=" * 80)


def imprimir_resultados(resultados: list[ResultadoVerificacao]) -> None:
    for resultado in resultados:
        print(f"[{resultado.status}] {resultado.item}: {resultado.detalhe}")


def tem_erro(resultados: list[ResultadoVerificacao]) -> bool:
    return any(resultado.status == "ERRO" for resultado in resultados)


def executar_etapa(nome: str, funcao: Callable[[], object]) -> object:
    imprimir_etapa(nome)
    resultado = funcao()
    if isinstance(resultado, tuple):
        for indice, item in enumerate(resultado, start=1):
            if isinstance(item, pd.DataFrame):
                print(f"saida_{indice}: {item.shape}")
    elif isinstance(resultado, dict):
        for chave, item in resultado.items():
            if isinstance(item, pd.DataFrame):
                print(f"{chave}: {item.shape}")
            else:
                print(f"{chave}: {item}")
    elif resultado is not None:
        print(resultado)
    return resultado


def checar_pre_requisitos() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    resultados.extend(verificar_documentacao_fonte())
    resultados.extend(verificar_fonte_publica_online())
    resultados.extend(verificar_arquivos_brutos())
    return resultados


def atualizar_projeto() -> int:
    imprimir_etapa("1. Verificacao inicial")
    anos = resolver_anos_analise()
    print(f"Anos que serao processados: {anos}")

    resultados_iniciais = checar_pre_requisitos()
    imprimir_resultados(resultados_iniciais)
    if tem_erro(resultados_iniciais):
        print()
        print("Atualizacao interrompida: corrija os erros de pre-requisito antes de reprocessar.")
        return 1

    executar_etapa("2. Limpeza e tratamento dos dados", lambda: gerar_tratados(anos=anos))
    executar_etapa("3. Modelagem dos dados", gerar_modelados)
    executar_etapa("4. Recalculo dos indices de risco", gerar_indices)
    executar_etapa("4.1 Auditoria de dados", auditar_dados)

    imprimir_etapa("5. Verificacao final")
    resultados_finais = verificar_dados_publicos()
    imprimir_relatorio(resultados_finais)

    if tem_erro(resultados_finais):
        print("Atualizacao concluida com erro(s) de verificacao. Revise o relatorio acima.")
        return 1

    print("Atualizacao concluida. Reabra ou recarregue o dashboard para visualizar os dados atualizados.")
    print("Comando do dashboard: python -m streamlit run dashboard/app.py")
    return 0


def main() -> int:
    return atualizar_projeto()


if __name__ == "__main__":
    raise SystemExit(main())
