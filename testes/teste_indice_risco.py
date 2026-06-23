import importlib

import pandas as pd

from src.calcular_indice_risco import calcular_indice_risco


def test_indice_risco_nao_negativo():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "uf": ["SP", "SP", "MG"],
        "mortos": [0, 1, 0],
        "feridos_graves": [2, 0, 1],
        "feridos_leves": [1, 1, 0],
    })
    risco = calcular_indice_risco(df, "uf")
    assert (risco["indice_risco"] >= 0).all()
    assert {"Baixo", "Médio", "Alto", "Crítico"}.intersection(set(risco["classe_risco"]))


def test_scripts_principais_importam_sem_erro():
    modulos = [
        "src.config",
        "src.carregar_dados",
        "src.limpar_dados",
        "src.criar_colunas_derivadas",
        "src.modelar_dados",
        "src.calcular_indice_risco",
        "src.gerar_graficos",
        "src.gerar_relatorio",
        "src.utils",
    ]
    for modulo in modulos:
        importlib.import_module(modulo)
