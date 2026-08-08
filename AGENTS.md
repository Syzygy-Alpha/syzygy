# SYZYGY — AGENTS.md

> Documento permanente de contexto e regras para agentes de desenvolvimento.
>
> Este arquivo define a identidade, arquitetura, princípios e limites do projeto SYZYGY.
>
> **Leia este arquivo antes de modificar qualquer código.**
>
> Este documento possui precedência sobre decisões implícitas feitas pelo agente durante uma tarefa. Uma tarefa específica pode adicionar requisitos, mas não deve contradizer esta arquitetura sem uma decisão arquitetural explícita.

---

# 1. O que é o SYZYGY

**SYZYGY** é uma plataforma pessoal distribuída, modular e evolutiva.

Seu objetivo de longo prazo é integrar:

* dispositivos;
* arquivos;
* projetos;
* conhecimento;
* aplicações;
* automações;
* agentes de IA;
* infraestrutura;
* observabilidade;
* segurança;

em um único ecossistema controlado pelo usuário.

SYZYGY não deve ser tratado simplesmente como:

* uma aplicação web;
* um chatbot;
* um gerenciador de arquivos;
* um sistema de automação;
* um conjunto aleatório de microsserviços.

Ele é uma **plataforma pessoal digital**.

---

# 2. Visão de longo prazo

A visão do projeto é permitir que múltiplos dispositivos funcionem como partes de um mesmo ecossistema:

```text
                    SYZYGY
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     Desktop        Notebook        Phone
        │              │              │
        └──────────────┼──────────────┘
                       │
              ┌────────▼────────┐
              │    Mycelium     │
              │ Distributed Mesh│
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
         NAS         Server        IoT
```

No futuro, novos nós poderão ser adicionados sem que a arquitetura precise ser reconstruída.

---

# 3. Princípios fundamentais

## 3.1 Local-first

O sistema deve funcionar localmente sempre que possível.

Cloud é uma extensão, não uma dependência fundamental.

---

## 3.2 Soberania digital

Priorizar:

* open source;
* self-hosting;
* formatos abertos;
* armazenamento local;
* controle dos próprios dados;
* possibilidade de substituir serviços externos.

Não criar dependência obrigatória de SaaS proprietário sem justificativa.

---

## 3.3 Modularidade

Cada módulo possui uma responsabilidade própria.

Não mover funcionalidades entre módulos arbitrariamente.

---

## 3.4 Baixo acoplamento

Módulos devem depender de contratos bem definidos.

Preferir:

```text
API
EventBus
interfaces
protocolos
```

em vez de acessar diretamente a implementação interna de outro módulo.

---

## 3.5 Event-driven

Quando apropriado, mudanças de estado devem ser comunicadas através de eventos.

Exemplo:

```text
Mycelium
    │
    ▼
DeviceConnected
    │
    ▼
Foundation EventBus
    ├── Observatory
    ├── NERV
    └── outros consumidores
```

---

## 3.6 Segurança por padrão

Nunca:

* commitar secrets;
* colocar API keys no código;
* colocar senhas em arquivos versionados;
* registrar tokens nos logs;
* assumir que a rede local é automaticamente confiável.

---

## 3.7 Observabilidade

Serviços devem possuir, quando aplicável:

* healthcheck;
* logs;
* versão;
* estado;
* métricas futuras;
* tracing futuro.

---

## 3.8 Evolução incremental

O projeto deve crescer em pequenos incrementos funcionais.

Não implementar funcionalidades futuras apenas porque elas estão previstas na visão.

---

# 4. Regra contra alucinação arquitetural

Antes de criar uma nova tecnologia, módulo, serviço ou abstração, pergunte:

1. Isso já existe na arquitetura?
2. Qual módulo é responsável por isso?
3. Essa funcionalidade pertence realmente ao módulo atual?
4. Existe alguma dependência circular?
5. Isso é necessário para o MVP atual?
6. Existe uma solução mais simples?
7. Essa decisão contradiz algum documento do projeto?

Se a resposta não estiver clara:

**não invente.**

Documente a dúvida e proponha uma decisão.

---

# 5. Módulos oficiais

Os módulos oficiais do SYZYGY são:

```text
Foundation
Mycelium
Coppermind
MAGI
Balance
Tungsten
Forge
Observatory
Imrryr
NERV
Elric
Bastion
```

Não criar novos módulos de nível equivalente sem uma decisão arquitetural explícita.

---

# 6. Foundation

## Propósito

Núcleo técnico compartilhado do SYZYGY.

## Responsabilidades

* configuração;
* identidade;
* autenticação;
* autorização básica;
* EventBus;
* Scheduler;
* APIs internas;
* Service Discovery;
* RPC;
* plugins;
* configuração distribuída;
* lifecycle dos módulos.

## MVP

* FastAPI;
* configuração;
* healthcheck;
* versionamento;
* SQLite;
* autenticação básica;
* EventBus;
* Scheduler;
* Docker.

## Tecnologias principais

```text
Python
FastAPI
NATS
Redis
SQLite
JWT
Docker
Pytest
```

---

# 7. Mycelium

## Propósito

Rede distribuída do SYZYGY.

## Responsabilidades

* descoberta;
* sincronização;
* replicação;
* backup;
* comunicação entre nós;
* versionamento distribuído;
* cache compartilhado.

## Agente

```text
Hypha
```

## Tecnologias previstas

```text
Syncthing
WireGuard
Tailscale
gRPC
SQLite
NATS
```

---

# 8. Coppermind

## Propósito

Memória permanente do SYZYGY.

## Responsabilidades

* documentos;
* notas;
* código;
* conversas;
* livros;
* PDFs;
* OCR;
* embeddings;
* RAG;
* Knowledge Graph;
* busca semântica.

## Agentes

```text
Archivist
Indexer
Curator
Historian
Librarian
```

## Tecnologias previstas

```text
SQLite
Markdown
ChromaDB / Qdrant
Ollama
LangChain
```

---

# 9. MAGI

## Propósito

Conselho de inteligência especializada.

## Componentes

### Melchior

```text
Lógica
Arquitetura
Engenharia
Planejamento
```

### Balthasar

```text
Criatividade
Design
Brainstorm
Inovação
```

### Casper

```text
Comunicação
UX
Interação
Linguagem
```

## Tecnologias previstas

```text
Ollama
OpenRouter
MCP
LangGraph
```

---

# 10. Balance

## Propósito

Governança e tomada de decisão.

## Componentes

### Chaos

```text
Exploração
Criatividade
Alternativas
```

### Law

```text
Segurança
Políticas
Restrições
```

### Equilibrium

```text
Conciliação
Avaliação
Decisão final
```

---

# 11. Tungsten

## Propósito

Infraestrutura de confiança e segurança.

## Responsabilidades

* secrets;
* vault;
* API keys;
* MFA;
* certificados;
* criptografia;
* PKI;
* auditoria;
* controle de acesso.

## Tecnologias previstas

```text
HashiCorp Vault
OpenSSL
Keycloak
```

---

# 12. Forge

## Propósito

Engenharia de software e automação.

## Responsabilidades

* Git;
* projetos;
* builds;
* deploy;
* containers;
* DevContainers;
* CI/CD;
* templates;
* agentes de programação.

---

# 13. Observatory

## Propósito

Observabilidade do ecossistema.

## Responsabilidades

* logs;
* métricas;
* tracing;
* dashboards;
* alertas;
* telemetria.

## Tecnologias previstas

```text
Grafana
Prometheus
Loki
```

---

# 14. Imrryr

## Propósito

Workspace de aplicações próprias e experimentais.

Exemplos futuros:

```text
Vim próprio
Markdown Editor
Obsidian próprio
PDF Manager
Media Player
Terminal
Explorer
SSH Client
Hex Editor
```

## Tecnologias previstas

```text
React
Tauri
Flutter
Electron somente quando necessário
```

---

# 15. NERV

## Propósito

Centro operacional do SYZYGY.

## Responsabilidades

* dashboard;
* dispositivos;
* serviços;
* containers;
* agentes;
* operações;
* estado do sistema.

## Tecnologias previstas

```text
React
Material UI
WebSockets
```

---

# 16. Elric

## Propósito

Representação do usuário dentro do ecossistema.

## Responsabilidades

* perfil;
* preferências;
* contexto;
* histórico;
* jornada;
* personalização.

Elric deve ser integrado ao Foundation, não duplicar mecanismos fundamentais de identidade.

---

# 17. Bastion

## Propósito

Laboratório isolado de segurança.

## Responsabilidades

* segurança ofensiva autorizada;
* segurança defensiva;
* CTF;
* reverse engineering;
* malware analysis em ambiente isolado;
* honeypots;
* análise de vulnerabilidades;
* hardening;
* threat intelligence;
* forense;
* validação de segurança do próprio SYZYGY.

## Tecnologias previstas

```text
Kali Linux
Parrot OS
QEMU/KVM
VirtualBox
Docker
Wireshark
Suricata
Zeek
Ghidra
Burp Suite Community
Metasploit Framework
Velociraptor
YARA
Python
Rust
```

Toda atividade ofensiva deve permanecer em ambientes autorizados e controlados.

---

# 18. Relação entre módulos

A arquitetura conceitual é:

```text
                         ELRIC
                           │
                           ▼
                          NERV
                           │
                           ▼
                       FOUNDATION
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      MYCELIUM          FORGE         OBSERVATORY
          │                                 │
          ▼                                 │
      TUNGSTEN ◄────────────────────────────┘
          │
          ▼
      COPPERMIND
          │
          ▼
         MAGI
          │
          ▼
       BALANCE
```

Esta representação é conceitual.

Não significa que cada módulo precise chamar diretamente o módulo abaixo dele.

---

# 19. Ordem de evolução

A ordem recomendada é:

```text
Documentação
      ↓
Foundation
      ↓
Forge
      ↓
Mycelium
      ↓
Observatory
      ↓
Tungsten
      ↓
Coppermind
      ↓
MAGI
      ↓
Balance
      ↓
NERV
      ↓
Elric
      ↓
Imrryr
      ↓
Bastion
```

Essa ordem pode mudar quando houver uma razão técnica clara.

Mudanças significativas devem ser documentadas.

---

# 20. Foundation é a primeira implementação

O primeiro software funcional do ecossistema é o Foundation.

Não começar por:

```text
LLM
RAG
Knowledge Graph
agentes
UI complexa
sincronização P2P
mobile
```

Primeiro construir infraestrutura.

---

# 21. Tecnologias preferenciais

Quando houver liberdade de escolha, considerar primeiro:

### Backend

```text
Python
FastAPI
```

### Comunicação

```text
NATS
gRPC
WebSockets quando apropriado
```

### Persistência

```text
SQLite inicialmente
```

### Containers

```text
Docker
Docker Compose
```

### IA

```text
Ollama
LangGraph
MCP
```

### Frontend

```text
React
Material UI
```

### Observabilidade

```text
Prometheus
Grafana
Loki
```

### Segurança

```text
Vault
Keycloak
OpenSSL
```

Não adicionar uma tecnologia simplesmente porque ela é popular.

---

# 22. Regras de dependências

Evitar:

```text
A → B → A
```

Dependências circulares são indesejadas.

Preferir:

```text
Foundation
    ↑
    │
outros módulos
```

ou comunicação por contratos/eventos.

---

# 23. Contratos

Contratos entre módulos devem ser explícitos.

Exemplos:

```text
Event
API
Message
Schema
Interface
```

Eventos devem possuir:

* nome;
* produtor;
* consumidor;
* payload;
* versão;
* finalidade.

---

# 24. Eventos fundamentais

Eventos iniciais previstos:

```text
ModuleStarted
ModuleStopped
ConfigUpdated
HealthChanged
DeviceConnected
DeviceDisconnected
BuildStarted
BuildCompleted
```

Não é necessário implementar todos imediatamente.

A existência nesta lista significa que são parte da visão arquitetural.

---

# 25. Código

Preferir código:

* simples;
* explícito;
* testável;
* modular;
* tipado quando apropriado;
* documentado quando necessário.

Evitar:

* abstrações prematuras;
* frameworks desnecessários;
* padrões complexos sem benefício;
* código mágico;
* dependências desnecessárias.

---

# 26. Testes

Todo comportamento importante deve possuir testes.

Preferir:

```text
unit tests
integration tests
```

Testes devem validar comportamento real.

Não criar testes artificiais apenas para aumentar cobertura.

---

# 27. Git

Utilizar Conventional Commits:

```text
feat:
fix:
docs:
refactor:
test:
perf:
ci:
style:
build:
chore:
```

Versionamento:

```text
MAJOR.MINOR.PATCH
```

Branches preferenciais:

```text
main
develop
feature/*
fix/*
release/*
hotfix/*
```

Se o projeto existente possuir outra estratégia, não alterá-la silenciosamente.

---

# 28. Documentação

Decisões arquiteturais relevantes devem ser documentadas.

Utilizar ADRs:

```text
ADR-001
ADR-002
ADR-003
...
```

Formato:

```text
Contexto
Decisão
Alternativas
Consequências
Status
```

---

# 29. Estrutura documental

O projeto deve possuir documentação suficiente para explicar:

```text
Vision
Architecture
Modules
Development
Events
ADRs
Roadmap
Contributing
```

O GitHub é a documentação técnica oficial.

O Notion pode funcionar como ferramenta complementar de planejamento, Kanban e organização.

---

# 30. Regra de compatibilidade com Notion

Os cards do Notion devem seguir o padrão:

```text
Propósito
Responsabilidades
MVP
Tecnologias sugeridas
Visão futura
```

Não contradizer a documentação oficial do projeto.

---

# 31. Ambientes

O sistema deverá futuramente suportar diferentes ambientes:

```text
development
test
staging
production
lab
```

O Bastion deve possuir ambientes isolados próprios.

---

# 32. Desenvolvimento multi-device

Uma das metas centrais do SYZYGY é permitir desenvolvimento e uso em múltiplos dispositivos.

Exemplo futuro:

```text
Desktop
   │
   │ projeto criado
   ▼
Mycelium
   │
   ▼
Notebook
```

Alterações poderão futuramente ser:

```text
commitadas
sincronizadas
indexadas
observadas
```

sem exigir serviços proprietários.

Essa é uma meta arquitetural importante.

---

# 33. O que o agente NÃO deve fazer

Não:

* reinventar a arquitetura;
* renomear módulos;
* criar módulos sem necessidade;
* implementar toda a visão futura;
* adicionar IA onde não é necessária;
* adicionar cloud obrigatória;
* criar dependências proprietárias sem justificativa;
* remover documentação existente sem verificar seu propósito;
* apagar código funcional sem explicar;
* alterar contratos silenciosamente;
* ignorar testes;
* ignorar segurança;
* criar secrets no repositório;
* assumir que uma tecnologia futura já está disponível.

---

# 34. Quando houver dúvida

Se houver ambiguidade:

### Caso simples

Escolha a alternativa mais simples e reversível.

### Caso arquitetural

Pare e proponha uma decisão.

### Caso destrutivo

Não execute automaticamente.

### Caso que altere contratos

Documente.

### Caso que contradiga este arquivo

Não faça silenciosamente.

---

# 35. Processo obrigatório antes de alterar código

Antes de implementar:

```text
1. Ler AGENTS.md
2. Inspecionar o repositório
3. Identificar módulo afetado
4. Identificar dependências
5. Identificar contratos existentes
6. Identificar testes existentes
7. Identificar documentação relevante
8. Planejar alteração
9. Implementar menor mudança necessária
10. Executar testes
11. Atualizar documentação
```

---

# 36. Processo obrigatório depois de alterar código

Depois de qualquer alteração significativa:

```text
1. Executar testes
2. Executar lint
3. Verificar tipos quando aplicável
4. Verificar Docker quando aplicável
5. Verificar documentação
6. Verificar se contratos foram preservados
7. Verificar se nenhuma responsabilidade foi deslocada
```

---

# 37. Definition of Done

Uma tarefa não está concluída simplesmente porque o código compila.

Ela deve:

* funcionar;
* possuir testes apropriados;
* respeitar a arquitetura;
* possuir documentação necessária;
* não introduzir dependências desnecessárias;
* não quebrar contratos existentes;
* manter segurança básica;
* ser reproduzível.

---

# 38. Regra de escopo

Sempre diferenciar:

```text
NOW
```

do que é:

```text
FUTURE
```

Uma funcionalidade descrita na visão futura não deve ser implementada automaticamente.

Exemplo:

```text
COPPERMIND
```

possuir RAG na visão futura não significa que o Foundation deva possuir RAG.

---

# 39. Estado esperado do projeto

O SYZYGY deve evoluir aproximadamente assim:

```text
                    VISION
                       │
                       ▼
                 ARCHITECTURE
                       │
                       ▼
                  FOUNDATION
                       │
                       ▼
              DISTRIBUTED SYSTEM
                       │
                       ▼
                   KNOWLEDGE
                       │
                       ▼
                 INTELLIGENCE
                       │
                       ▼
                  GOVERNANCE
                       │
                       ▼
                 APPLICATIONS
                       │
                       ▼
             PERSONAL PLATFORM
```

---

# 40. Regra final

O objetivo não é escrever o máximo de código.

O objetivo é construir uma plataforma que continue fazendo sentido daqui a:

```text
6 meses
1 ano
5 anos
```

Toda decisão deve considerar:

> "Esta decisão facilita ou dificulta a evolução do SYZYGY?"

Quando duas soluções forem tecnicamente equivalentes, prefira a que:

1. é mais simples;
2. é mais aberta;
3. é mais local;
4. é mais reversível;
5. possui menos dependências;
6. preserva melhor a modularidade.

---

# 41. Resumo absoluto

Se houver apenas uma coisa para lembrar deste arquivo:

> **SYZYGY é uma plataforma pessoal distribuída, modular, local-first e orientada à soberania digital.**

E:

> **Foundation é a base. Os demais módulos devem crescer sobre contratos claros, sem transformar a visão futura em complexidade prematura.**

Não invente.

Não antecipe.

Não acople.

Não faça overengineering.

Construa incrementalmente.

Preserve a arquitetura.

Teste.

Documente.

E sempre mantenha o sistema evolutivo.
