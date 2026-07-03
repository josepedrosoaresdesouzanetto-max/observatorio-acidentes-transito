from __future__ import annotations

from datetime import date
from typing import Iterable


def ano_atual(data_referencia: date | None = None) -> int:
    """Retorna o ano corrente usado para identificar recortes ainda parciais."""
    return (data_referencia or date.today()).year


def anos_parciais(anos: Iterable[int], data_referencia: date | None = None) -> tuple[int, ...]:
    """Considera parcial apenas o ano corrente, quando ele estiver no recorte."""
    atual = ano_atual(data_referencia)
    return tuple(sorted({int(ano) for ano in anos if int(ano) == atual}))


def anos_fechados(anos: Iterable[int], data_referencia: date | None = None) -> tuple[int, ...]:
    """Retorna anos anteriores ao ano corrente, tratados como recortes fechados."""
    atual = ano_atual(data_referencia)
    return tuple(sorted({int(ano) for ano in anos if int(ano) < atual}))


def texto_anos_parciais(anos: Iterable[int], data_referencia: date | None = None) -> str:
    parciais = anos_parciais(anos, data_referencia)
    if not parciais:
        return "Nao ha ano corrente no recorte; os anos disponiveis sao tratados como fechados."
    if len(parciais) == 1:
        return f"{parciais[0]} e parcial por ser o ano corrente."
    return f"{', '.join(str(ano) for ano in parciais)} sao parciais por estarem em andamento."
