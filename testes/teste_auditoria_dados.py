from src.auditar_dados import COLUNAS_BRUTAS_OCORRENCIA, sha256_arquivo


def test_sha256_arquivo(tmp_path):
    path = tmp_path / "amostra.csv"
    path.write_text("abc", encoding="utf-8")

    assert sha256_arquivo(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_colunas_obrigatorias_ocorrencia_incluem_variaveis_de_gravidade():
    assert {"id", "uf", "mortos", "feridos_graves", "feridos_leves"}.issubset(COLUNAS_BRUTAS_OCORRENCIA)
