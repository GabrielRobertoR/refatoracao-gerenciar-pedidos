# Refatoração de `GerenciadorPedidos`

## Code smells identificados

1. **Long Method** — `processar_pedido` mistura validação, cálculo, estoque, persistência e notificação.
2. **Large Class / responsabilidades excessivas** — a classe administra pedidos, estoque, cálculo, persistência, notificações e relatórios.
3. **Long Parameter List** — `processar_pedido` recebe dez parâmetros, incluindo cinco campos de endereço.
4. **Duplicated Code** — o cálculo de subtotal, descontos e frete aparece em `processar_pedido` e `calcular_orcamento`.
5. **Repeated Conditionals** — os tipos `COMUM`, `VIP` e `FUNCIONARIO` são tratados repetidamente em vários métodos.
6. **Primitive Obsession** — itens e histórico são armazenados em listas/strings posicionais.
7. **Acoplamento com infraestrutura** — a classe escreve diretamente em `pedidos.csv` e simula envio de e-mail usando `print`.

## Processo de caracterização

Os testes foram adicionados antes das refatorações. Eles registram respostas de erro, cálculos, limites, efeitos colaterais, conteúdo do arquivo, histórico e mensagens impressas.

## Histórico de refatoração e relação com SOLID

- Extração do subtotal: **SRP**, pois isola uma operação de cálculo nomeada e reutilizável.
- Extração do desconto: **SRP**, pois centraliza uma regra de negócio e remove sua duplicação.
- Extração do frete: **SRP**, pois isola outra regra de cálculo. O parâmetro `incluir_ma` preserva a diferença histórica entre orçamento e processamento; isso é intencional nesta atividade de caracterização.
- Extração do cálculo de pagamento: **SRP**, pois isola as regras de pagamento do fluxo de processamento.
- Extração da persistência CSV: **SRP**, pois isola a responsabilidade de gravar o pedido. A dependência concreta de arquivo ainda existe, então não afirmamos que o DIP foi totalmente aplicado.
- Extração da notificação: **SRP**, pois separa a montagem/impressão da mensagem do fluxo principal. A implementação ainda usa `print`; uma abstração injetável seria um passo adicional para DIP.

## Executar

```bash
python -m pip install pytest
python -m pytest -v
```

## Observação de escopo

Esta atividade busca refatorar sem alterar o comportamento observável. Por isso, a diferença já existente para o frete do estado `MA` entre `calcular_orcamento` e `processar_pedido` foi mantida e caracterizada em teste. Uma correção dessa regra seria uma mudança funcional separada.
