from datetime import date

from src.recorte_temporal import anos_fechados, anos_parciais, texto_anos_parciais


def test_identifica_apenas_ano_corrente_como_parcial():
    anos = (2024, 2026, 2027)
    referencia = date(2027, 3, 10)

    assert anos_parciais(anos, referencia) == (2027,)
    assert anos_fechados(anos, referencia) == (2024, 2026)


def test_texto_sem_ano_corrente_no_recorte():
    texto = texto_anos_parciais((2024, 2025), date(2027, 1, 5))

    assert "tratados como fechados" in texto
