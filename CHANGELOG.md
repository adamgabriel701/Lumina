# Changelog

Todas as mudanças relevantes do **Lumina** são documentadas neste arquivo.

O formato segue, de forma geral, as convenções do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

> Desenvolvimento posterior ao milestone `v0.5.0-linker`.

### ✨ Adicionado

#### Otimizador O1 integrado

* Integração do otimizador **O1** diretamente no pipeline de compilação.
* Otimização aplicada de forma integrada ao fluxo de geração de código.
* Preservação do comportamento semântico dos programas durante a otimização.

#### Pattern Matching de Structs

* Suporte a **desestruturação de structs** em padrões.
* Pattern matching de campos de structs.
* Integração dos padrões de structs ao sistema existente de `match`.
* Novos testes cobrindo os casos de pattern matching adicionados.

#### Sugestões automáticas

* Sistema de sugestões automáticas para identificadores desconhecidos.
* Implementação baseada em **distância de Levenshtein**.
* Mensagens de erro mais úteis para nomes digitados incorretamente.
* Sugestões integradas ao diagnóstico semântico.

#### Tipos de função

* Suporte a tipos de função no formato:

```text
fn(T1, T2) -> R
```

* Integração dos tipos de função ao sistema de tipos.
* Suporte a múltiplos parâmetros.
* Suporte a tipo de retorno explícito.
* Integração com closures e callbacks.

#### Closures como callbacks

* Closures podem ser utilizadas como callbacks.
* Unificação da representação de funções e closures por meio de ponteiros `fn`.
* Suporte a funções de primeira classe em APIs que recebem callbacks.

#### Escape sequences

* Suporte a sequências de escape em strings.
* Integração das novas sequências com lexer, parser e codegen.

#### Macros com múltiplas instruções

* Macros podem conter múltiplas instruções.
* Melhor integração das macros com o parser e o restante do pipeline.

#### Tail Call Optimization

* Suporte a **TCO (Tail Call Optimization)** para chamadas recursivas diretas.
* Redução do crescimento da stack em casos de recursão em posição de cauda.

#### LSP

* Novos **inlay hints**.
* Novas **code actions**.
* Melhor integração dos recursos de análise do compilador com o Language Server.

#### Cross-compilation

* Suporte ao parâmetro:

```text
--target=<triple>
```

* Testes de cross-compilation para arquiteturas adicionais.
* Validação de execução de binários cross-compilados utilizando QEMU.

#### CLI

* Propagação correta dos códigos de saída dos programas executados.
* Melhor integração das novas opções do compilador com o pipeline de build.

---

### 🔧 Alterado

#### Pipeline de compilação

* Refatoração de componentes internos do parser.
* Refatoração da análise semântica.
* Refatoração do codegen em componentes mais especializados.
* Melhor separação de responsabilidades entre as etapas do compilador.
* Integração mais consistente entre otimização, codegen e linking.

#### Sistema de tipos

* Expansão da cobertura de tipos.
* Melhor validação de tipos.
* Melhor integração entre tipos de função, closures e callbacks.
* Ampliação dos testes end-to-end relacionados ao sistema de tipos.

#### `match`

* Melhorias no parser e na análise semântica de expressões `match`.
* Expansão para padrões envolvendo structs.

#### Codegen

* Correções em diferentes caminhos de geração de código LLVM.
* Melhor tratamento de funções que terminam após determinadas operações de retorno.
* Correções relacionadas ao gerenciamento de stack em determinados padrões de código.
* Melhor integração com o runtime freestanding.

#### Runtime

* Expansão e correção de componentes do runtime.
* Melhor integração entre o runtime e o linker próprio.
* Correções em operações utilizadas pelos exemplos e testes do projeto.

---

### 🐛 Corrigido

#### `chip8`

* Corrigido um caminho de geração de código no qual `main` poderia terminar sem uma instrução `ret` adequada após determinadas operações.
* O problema tornou-se observável durante a utilização do linker próprio e do runtime freestanding.

#### `gc_test`

* Corrigido um problema relacionado à utilização de `alloca` dentro de loops.
* A implementação anterior poderia provocar crescimento contínuo da stack.
* O problema foi identificado durante os testes com o pipeline utilizando o linker próprio.

#### Codegen

* Correções em casos específicos de geração de código.
* Melhor tratamento de retornos em funções.
* Correções expostas pelos testes end-to-end utilizando o linker próprio.

#### Linker

* Correções no tratamento de símbolos `SHN_COMMON`.
* Adição/tratamento de símbolos sintéticos necessários durante o linking.
* Correções no layout dos segmentos `PT_LOAD`.
* Correções relacionadas à integração com o runtime freestanding.

#### Exemplos

* Correções necessárias para que os exemplos possam ser compilados e executados pelos diferentes pipelines disponíveis.
* Melhorias na triagem automática dos exemplos.

---

### 🧪 Testes

A suíte de testes foi ampliada continuamente durante o desenvolvimento.

Estado atual informado pelo projeto:

```text
pytest tests/ -q
440 passed
```

Verificações adicionais:

```text
python3 run_tests.py
28/28 verifications OK
```

Execução dos exemplos:

```text
./scripts/check_examples.sh --run
54 PASS / 17 SKIP / 0 FAIL
```

Triagem do linker próprio:

```text
./linker/triagem.sh examples
PASS=53 FAIL-COMPILE=0 FAIL-LINK=0 FAIL-RUN=0 SKIP=18
```

Os números de exemplos ignorados diferem entre os scripts porque as duas verificações possuem escopos diferentes.

---

### 📚 Documentação

* Documentação do linker próprio adicionada em:

```text
docs/internals/linking.md
```

* Documentada a arquitetura interna do `lumina-ld`.

* Documentadas as fases do processo de linking.

* Documentado o processo de resolução de símbolos.

* Documentado o layout do executável.

* Documentado o processo de relocação.

* Documentada a geração do ELF final.

* Documentados símbolos sintéticos.

* Documentada a integração do linker com a CLI.

* Documentado o runtime freestanding.

* Documentados pontos de extensão e debugging do linker.

* README atualizado com:

  * status do compilador;
  * linker próprio;
  * runtime freestanding;
  * testes;
  * exemplos;
  * benchmarks;
  * limitações;
  * arquitetura do projeto.

---

## [0.5.0-linker] — 2026-09-23

> **Milestone:** linker próprio + runtime freestanding.

Esta versão representa a introdução do pipeline de linking próprio do Lumina para executáveis ELF x86_64 Linux.

### ✨ Adicionado

#### Linker próprio — `lumina-ld`

* Novo linker estático próprio implementado em C.
* Suporte inicial a:

```text
ET_REL → ET_EXEC
```

* Pipeline dividido em cinco fases principais:

  1. parsing;
  2. resolução de símbolos;
  3. layout;
  4. relocação;
  5. escrita do ELF final.

* Suporte inicial à arquitetura:

```text
x86_64
```

* Geração de executáveis ELF.
* Integração do linker ao pipeline do compilador.

#### Relocações

Suporte às seguintes relocações x86_64:

```text
R_X86_64_64
R_X86_64_PC32
R_X86_64_PLT32
R_X86_64_32
R_X86_64_32S
R_X86_64_PC64
```

* Suporte a relaxações relacionadas a:

```text
GOTPCREL
GOTPCRELX
REX_GOTPCRELX
```

#### Runtime freestanding

* Novo runtime sem dependência de libc para o pipeline do linker próprio.
* Implementação de `_start` em assembly x86_64.
* Utilização direta de syscalls Linux.
* Suporte a operações básicas de memória.
* Operações de strings.
* Console e file descriptors.
* I/O de arquivos.
* Operações matemáticas.
* Geração de números aleatórios.
* `sleep`.
* Sockets.
* `epoll`.
* Suporte relacionado a coroutines.
* Suporte relacionado a threads.
* Shims necessários para o garbage collector.

Arquivos principais:

```text
start.S
rt.c
```

#### CLI

* Novo modo:

```text
--linker=self
```

* Permite selecionar o linker próprio do Lumina.
* O pipeline compila os objetos utilizando LLVM/Clang e realiza o linking final com:

```text
linker/lumina-ld
```

* O cache de compilação passa a considerar o tipo de linker utilizado.
* O modo com linker próprio utiliza `--no-gc` implicitamente quando necessário ao pipeline.

#### Testes de integração

* Adicionado suporte à execução dos exemplos utilizando o linker próprio.
* Criada triagem específica para distinguir:

  * falhas de compilação;
  * falhas de linking;
  * falhas de execução;
  * exemplos ignorados.

---

### 🔧 Alterado

#### Linking

* O projeto passa a possuir duas estratégias de linking:

  * pipeline convencional baseado em Clang;
  * linker próprio do Lumina.

* O linker próprio é direcionado ao ambiente:

```text
Linux x86_64
```

* Recursos de cross-compilation e WASM continuam utilizando as ferramentas LLVM/Clang apropriadas.

#### Runtime

* Separação mais clara entre funcionalidades dependentes de libc e o runtime freestanding.
* Adaptação de funcionalidades para execução através de syscalls Linux.

---

### 🐛 Corrigido

#### Runtime

* Corrigidos componentes necessários para execução de programas sem libc.
* Adicionados símbolos e funções necessárias para aplicações reais do projeto.

#### Codegen

* Corrigido o problema de stack overflow observado em `gc_test`.
* Corrigido o caminho de geração de código que poderia deixar `chip8` sem retorno adequado.

---

### 🧪 Testes

Estado documentado no desenvolvimento deste milestone:

```text
54 PASS
17 SKIP
0 FAIL
```

O pipeline convencional e o pipeline utilizando o linker próprio foram comparados durante a validação.

---

## Histórico anterior

> As versões abaixo representam funcionalidades e marcos anteriores do projeto conforme documentados durante o desenvolvimento. Detalhes adicionais devem ser mantidos apenas quando correspondentes aos respectivos tags/releases existentes no repositório.

### Desenvolvimento anterior — Setembro de 2026

#### Sistema de funções

* Adicionados tipos de função:

```text
fn(T1, T2) -> R
```

* Suporte a funções como valores.
* Suporte a callbacks.
* Integração com closures.

#### Closures

* Closures passaram a poder ser utilizadas como callbacks.
* Representação unificada por meio de ponteiros `fn`.

#### Parser e semântica

* Refatoração do parser em componentes especializados.
* Refatoração da análise semântica.
* Refatoração do codegen.
* Melhor organização interna do compilador.

#### Pattern matching

* Expansão do sistema de `match`.
* Melhorias na análise semântica.
* Maior cobertura de testes.

#### Operadores

* Expansão do suporte a operadores bitwise.
* Correções no parser e codegen associados.

#### TCO

* Implementação de tail-call optimization para recursão direta em posição de cauda.

#### LSP

* Suporte a inlay hints.
* Suporte a code actions.
* Melhor integração entre diagnósticos do compilador e editor.

#### Cross-compilation

* Introdução do parâmetro:

```text
--target=<triple>
```

* Validação de targets alternativos.
* Testes com QEMU para execução de binários destinados a arquiteturas diferentes.

#### CLI

* Melhor tratamento de códigos de saída.
* Correções no comportamento de comandos de execução.

#### Testes

* Expansão progressiva da suíte de testes.
* Testes de integração end-to-end.
* Testes de tipos.
* Testes de parser.
* Testes de codegen.
* Testes de exemplos completos.

---

## Convenções

As mudanças são agrupadas nas seguintes categorias:

* **✨ Adicionado** — novas funcionalidades.
* **🔧 Alterado** — mudanças em funcionalidades existentes.
* **🐛 Corrigido** — correções de bugs.
* **🧪 Testes** — mudanças na infraestrutura ou cobertura de testes.
* **📚 Documentação** — mudanças exclusivamente documentais.
* **⚡ Performance** — melhorias de desempenho.
* **🗑️ Removido** — funcionalidades removidas.
* **🔒 Segurança** — correções relacionadas à segurança.

---

## Links

* [Repositório](https://github.com/adamgabriel701/Lumina)
* [Milestone `v0.5.0-linker`](https://github.com/adamgabriel701/Lumina/releases/tag/v0.5.0-linker)

[Unreleased]: https://github.com/adamgabriel701/Lumina/compare/v0.5.0-linker...HEAD
[0.5.0-linker]: https://github.com/adamgabriel701/Lumina/releases/tag/v0.5.0-linker