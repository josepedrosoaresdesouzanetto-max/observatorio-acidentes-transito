from src.verificar_dados_publicos import ResultadoVerificacao, extrair_arquivos_publicos_prf, salvar_relatorio


def test_extrai_arquivos_publicos_prf_sem_baixar_planilhas():
    html = """
    <html>
      <body>
        <p>Documento CSV de Acidentes 2027 (Agrupados por ocorrência)</p>
        <a href="/ocorrencia-2027.csv">Baixar planilha</a>
        <p>Documento CSV de Acidentes 2027 (Agrupados por pessoa)</p>
        <a href="/pessoa-2027.csv">Baixar planilha</a>
        <p>Documento CSV de Acidentes 2027 (Agrupados por pessoa - Todas as causas e tipos de acidentes)</p>
        <a href="/pessoa-2027-todas.csv">Baixar planilha</a>
      </body>
    </html>
    """

    arquivos = extrair_arquivos_publicos_prf(html, base_url="https://exemplo.gov.br/dados/")

    assert [(arquivo.ano, arquivo.tipo) for arquivo in arquivos] == [(2027, "ocorrencia"), (2027, "pessoa")]
    assert arquivos[0].url == "https://exemplo.gov.br/ocorrencia-2027.csv"


def test_salva_relatorio_de_status(tmp_path):
    destino = tmp_path / "status.md"
    resultados = [ResultadoVerificacao("OK", "Item testado", "Detalhe validado.")]

    path = salvar_relatorio(resultados, destino)

    assert path == destino
    texto = destino.read_text(encoding="utf-8")
    assert "# Verificacao de dados publicos" in texto
    assert "[OK] Item testado: Detalhe validado." in texto
