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

A suíte inicial de caracterização foi adicionada antes das refatorações e registra respostas de erro, cálculos, limites, efeitos colaterais, conteúdo do arquivo, histórico e mensagens impressas. Uma verificação complementar do frete para `MA` foi adicionada depois, para reforçar a preservação dessa diferença histórica.

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

### Commits realizados

1. `chore: add original order manager` — preserva a versão inicial.
2. `test: characterize existing order manager behavior` — adiciona a suíte inicial antes das refatorações.
3. `refactor: extract order subtotal calculation` — extrai subtotal; aproxima o código do SRP e reduz o método longo.
4. `refactor: centralize customer discount rules` — remove duplicação das regras de desconto; melhora coesão e aproxima o SRP.
5. `refactor: extract shipping cost calculation` — isola o cálculo do frete; melhora coesão e aproxima o SRP.
6. `refactor: extract payment total calculation` — isola o cálculo do pagamento; melhora coesão e aproxima o SRP.
7. `refactor: extract order persistence and notification` — extrai operações para métodos nomeados; reduz o tamanho de `processar_pedido`.
8. `refactor: isolate CSV persistence in repository` — cria um repositório dedicado, restaurando SRP no que diz respeito à persistência e permitindo substituição por injeção.
9. `refactor: isolate order notification service` — cria um notificador dedicado, restaurando SRP no que diz respeito à notificação e permitindo substituição por injeção.
10. `test: cover regional freight behavior and document refactoring` — adiciona teste complementar e documenta a análise.
11. `chore: ignore Python test artifacts` — evita que caches locais sejam incluídos no repositório.

Os passos 3–7 melhoram a separação de responsabilidades dentro da classe, mas não eliminam sozinhos o smell de classe com múltiplas responsabilidades. Os passos 8–9 separam essas responsabilidades em colaboradores distintos. A injeção de repositório/notificador prepara o código para DIP e testes com dublês; a criação padrão dos colaboradores ainda instancia implementações concretas, portanto o DIP pode ser aprofundado com Protocols/abstrações e composição externa.
