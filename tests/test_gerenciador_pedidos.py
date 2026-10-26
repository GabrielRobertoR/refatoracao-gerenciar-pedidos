import pytest

from gerenciador_pedidos import GerenciadorPedidos


@pytest.fixture
def gerente():
    return GerenciadorPedidos()


def dados_pedido(**alteracoes):
    dados = {
        "nome": "Ana",
        "email": "ana@example.com",
        "tipo_cliente": "COMUM",
        "pagamento": "PIX",
        "parcelas": 1,
        "rua": "Rua A",
        "numero": "10",
        "cidade": "Recife",
        "uf": "PE",
        "cep": "50000-000",
    }
    dados.update(alteracoes)
    return dados


def processar(gerente, **alteracoes):
    return gerente.processar_pedido(**dados_pedido(**alteracoes))


def test_estoque_inicial(gerente):
    assert gerente.estoque == {
        "CANETA": 100,
        "CADERNO": 50,
        "MOCHILA": 10,
        "CALCULADORA": 5,
    }


def test_adicionar_item_guarda_quantidade_e_preco_como_strings(gerente):
    gerente.adicionar_item("CANETA", 2, 3.50)
    assert gerente.itens == [["CANETA", "2", "3.5"]]


def test_orcamento_comum_pe_com_item_de_20_reais(gerente):
    gerente.adicionar_item("CANETA", 2, 10)
    assert gerente.calcular_orcamento("COMUM", "PE") == 32.5


def test_orcamento_vip_aplica_dez_porcento_abaixo_de_500(gerente):
    gerente.adicionar_item("CANETA", 2, 50)
    assert gerente.calcular_orcamento("VIP", "PE") == 90.0


def test_orcamento_comum_nao_aplica_desconto_quando_subtotal_e_500(gerente):
    gerente.adicionar_item("CANETA", 10, 50)
    assert gerente.calcular_orcamento("COMUM", "PE") == 500.0


def test_orcamento_comum_aplica_desconto_quando_subtotal_supera_500(gerente):
    gerente.adicionar_item("CANETA", 51, 10)
    assert gerente.calcular_orcamento("COMUM", "PE") == 484.5


def test_orcamento_nao_aplica_desconto_para_tipo_desconhecido(gerente):
    gerente.adicionar_item("CANETA", 1, 10)
    assert gerente.calcular_orcamento("DESCONHECIDO", "PE") == 22.5


def test_orcamento_para_ma_nao_usa_frete_regional(gerente):
    gerente.adicionar_item("CANETA", 1, 10)
    assert gerente.calcular_orcamento("COMUM", "MA") == 49.9


def test_processar_pedido_vazio_retorna_erro_sem_alterar_estado(gerente):
    resultado = processar(gerente)
    assert resultado == "ERRO: pedido vazio"
    assert gerente.total_vendido == 0
    assert gerente.historico == []


@pytest.mark.parametrize(("campo", "valor", "esperado"), [
    ("nome", None, "ERRO: cliente sem nome"),
    ("nome", "   ", "ERRO: cliente sem nome"),
    ("email", None, "ERRO: email invalido"),
    ("email", "anaexample.com", "ERRO: email invalido"),
    ("cep", None, "ERRO: cep invalido"),
    ("cep", "123", "ERRO: cep invalido"),
])
def test_validacoes_iniciais(gerente, campo, valor, esperado):
    gerente.adicionar_item("CANETA", 1, 10)
    assert processar(gerente, **{campo: valor}) == esperado


def test_produto_inexistente_retorna_erro(gerente):
    gerente.adicionar_item("LAPIS", 1, 2)
    assert processar(gerente) == "ERRO: produto inexistente LAPIS"


def test_estoque_insuficiente_retorna_erro(gerente):
    gerente.adicionar_item("MOCHILA", 11, 10)
    assert processar(gerente) == "ERRO: estoque insuficiente MOCHILA"


def test_tipo_cliente_desconhecido_retorna_erro(gerente):
    gerente.adicionar_item("CANETA", 1, 10)
    assert processar(gerente, tipo_cliente="OUTRO") == "ERRO: tipo de cliente desconhecido"


def test_pagamento_desconhecido_retorna_erro(gerente):
    gerente.adicionar_item("CANETA", 1, 10)
    assert processar(gerente, pagamento="DINHEIRO") == "ERRO: forma de pagamento invalida"


@pytest.mark.parametrize("parcelas", [0, 13])
def test_cartao_com_parcelas_invalidas_retorna_erro(gerente, parcelas):
    gerente.adicionar_item("CANETA", 1, 10)
    assert processar(gerente, pagamento="CARTAO", parcelas=parcelas) == "ERRO: parcelas invalidas"


def test_processamento_pix_atualiza_estoque_historico_total_e_limpa_itens(gerente, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    gerente.adicionar_item("CANETA", 2, 10)

    resultado = processar(gerente)

    assert resultado == "OK: 30.88"
    assert gerente.estoque["CANETA"] == 98
    assert gerente.historico == ["Ana|COMUM|30.88"]
    assert gerente.total_vendido == 30.88
    assert gerente.itens == []
    assert (tmp_path / "pedidos.csv").read_text(encoding="utf-8") == (
        "Ana;ana@example.com;COMUM;PIX;30.88;Rua A, 10, Recife/PE, CEP 50000-000\n"
    )
    assert "[EMAIL para ana@example.com]" in capsys.readouterr().out


def test_boleto_adiciona_taxa_de_dois_reais_e_cinquenta(gerente, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    gerente.adicionar_item("CANETA", 1, 10)
    assert processar(gerente, pagamento="BOLETO") == "OK: 25.00"


def test_cartao_com_mais_de_tres_parcelas_aplica_taxa(gerente, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    gerente.adicionar_item("CANETA", 1, 100)
    assert processar(gerente, pagamento="CARTAO", parcelas=4) == "OK: 121.46"


def test_falha_ao_salvar_arquivo_nao_impede_pedido(monkeypatch, gerente, capsys):
    def falhar_open(*args, **kwargs):
        raise OSError("sem permissao")

    monkeypatch.setattr("builtins.open", falhar_open)
    gerente.adicionar_item("CANETA", 1, 10)

    resultado = processar(gerente)

    assert resultado == "OK: 21.38"
    assert "Falha ao salvar pedido: sem permissao" in capsys.readouterr().out
    assert gerente.historico == ["Ana|COMUM|21.38"]


def test_relatorio_sem_vendas(gerente):
    assert gerente.gerar_relatorio() == (
        "=== RELATORIO DE VENDAS ===\n"
        "Pedidos VIP: 0\n"
        "Pedidos COMUM: 0\n"
        "Pedidos FUNCIONARIO: 0\n"
        "Total vendido: R$ 0.00\n"
    )


def test_relatorio_contabiliza_tipos_e_meta(gerente):
    gerente.historico = ["Ana|VIP|5000.0", "Bia|COMUM|3000.0", "Caio|FUNCIONARIO|2500.0"]
    gerente.total_vendido = 10500.0

    relatorio = gerente.gerar_relatorio()

    assert "Pedidos VIP: 1" in relatorio
    assert "Pedidos COMUM: 1" in relatorio
    assert "Pedidos FUNCIONARIO: 1" in relatorio
    assert "Total vendido: R$ 10500.00" in relatorio
    assert "Meta mensal atingida!" in relatorio


def test_verificar_estoque_retorna_alertas_e_imprime_notificacao(gerente, capsys):
    gerente.estoque["CALCULADORA"] = 4

    alerta = gerente.verificar_estoque()

    assert alerta == "ALERTA: CALCULADORA com estoque baixo (4)\n"
    assert "[EMAIL para compras@loja.com] Repor CALCULADORA" in capsys.readouterr().out


def test_mensagem_promocional_por_tipo_de_cliente(gerente):
    assert gerente.mensagem_promocional("VIP") == "Ofertas exclusivas: 15% em compras acima de R$ 500!"
    assert gerente.mensagem_promocional("COMUM") == "Compre acima de R$ 500 e ganhe 5% de desconto!"
    assert gerente.mensagem_promocional("FUNCIONARIO") == "Lembrete: seu desconto de 20% vale em toda a loja."
    assert gerente.mensagem_promocional("OUTRO") == ""
