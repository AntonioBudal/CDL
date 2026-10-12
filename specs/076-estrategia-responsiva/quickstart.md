# Protocolo de Validação Responsiva — Quickstart

**Feature**: `076-estrategia-responsiva`  
**Objetivo**: Procedimento isolado e reproduzível para inspeção de layout e responsividade com banco de dados temporário.

---

## 1. Princípio Fundamental de Isolamento e Privacidade
- **NUNCA** execute validações contra o banco de dados ativo do usuário (`backend/data/caderno.db`).
- Toda verificação visual deve utilizar uma instância descartável e efêmera de banco SQLite apontada via variável de ambiente `CADERNO_DATABASE_PATH`.

---

## 2. Inicialização do Ambiente Efêmero

### Passo 1: Criar Diretório e Banco Descartável
No terminal PowerShell (Windows):

```powershell
$tempDir = Join-Path $env:TEMP ("caderno_valida_" + [System.Guid]::NewGuid().ToString().Substring(0,8))
New-Item -ItemType Directory -Path $tempDir -Force
$env:CADERNO_DATABASE_PATH = Join-Path $tempDir "valida_temp.db"
$env:CADERNO_PORT = "8899"
```

### Passo 2: Executar Migrações e Inicializar Backend
```powershell
# Executa aplicação em porta efêmera com isolamento total
python -m uvicorn app.main:app --app-dir caderno-leitura-0.1/backend --port 8899 --host 127.0.0.1
```

### Passo 3: Semeadura de Dados Sintéticos (Checklist T003)
Criar através da própria interface do usuário ou de script temporário:
- [x] **1 Conta Administradora Fictícia**: `admin_teste@exemplo.local` (perfil admin para testar `/admin`).
- [x] **1 Conta Leitora Comum**: `leitor_teste@exemplo.local`.
- [x] **1 Livro Fictício**: "Tratado de Testes e Estruturas".
- [x] **3 Capítulos**: "Capítulo 1: Fundações", "Capítulo 2: Variações", "Capítulo 3: Síntese".
- [x] **≥12 Estudos no Capítulo 1**:
  - Pelo menos 1 estudo marcado como "Núcleo" (Core).
  - Profundidade hierárquica na Árvore de até 5 níveis aninhados.
  - Pelo menos 8 relações semânticas com diferentes tipos (`supports`, `contradicts`, `expands`, `questions`).
  - 2 Molduras espaciais criadas na visualização em Canvas com estudos associados.

---

## 3. Matriz de Viewports Canônicas para Inspeção

Ao inspecionar no DevTools (ou navegador emulado):

| Identificador | Resolução | Modo / Dispositivo Típico | Aspectos Críticos a Inspecionar |
|---|---|---|---|
| **V-320** | 320 × 568 px | Tela compacta (iPhone SE 1ª gen) | Quebra de grids de 280px, profundidade na Árvore, alvos táteis. |
| **V-375** | 375 × 667 px | Móvel Padrão (iPhone SE / 8) | Header sem acúmulo de abas, barra inferior de 5 destinos, Map View. |
| **V-390** | 390 × 844 px | Móvel Moderno (iPhone 13/14) | Largura de popovers e modais, notificações, safe-area-inset. |
| **V-430** | 430 × 932 px | Móvel Pro Max | Dropdown de notificações, alinhamento de toolbars. |
| **V-767** | 767 × 1024 px | Limiar Superior Móvel | Comportamento móvel estrito antes do corte de tablet. |
| **V-768** | 768 × 1024 px | Limiar Inferior Tablet (iPad) | Transição para SplitLayout em drawer, Canvas com pinch/alças táteis. |
| **V-1023** | 1023 × 768 px | Tablet Paisagem | Persistência de gavetas e visualizações sem quebra lateral. |
| **V-1024** | 1024 × 768 px | Desktop Inicial / Split | Transição para SplitLayout com painéis fixos simultâneos. |
| **V-1440** | 1440 × 900 px | Desktop Amplo | Largura máxima do workspace (`74rem`), centralização e respiros. |
| **V-LAND** | 844 × 390 px | Móvel Paisagem | Visibilidade vertical, teclado virtual, altura útil de modais. |

---

## 4. Roteiro de Checagem por Tela

1. **Horizontal Scroll Check**: Inspecionar no console:
   ```javascript
   document.documentElement.scrollWidth > document.documentElement.clientWidth
   ```
   Deve retornar `false` em todas as rotas e viewports.
2. **Safe Area & Offsets**: Garantir que elementos fixos inferiores (`position: fixed`) respeitem `--mobile-nav-offset`.
3. **Alternância de Temas**: Validar em pelo menos um tema claro (`claro` ou `pergaminho`) e um tema escuro (`grafite` ou `noite-suave`).

---

## 5. Limpeza e Descarte
Ao finalizar a inspeção:
```powershell
Remove-Item -Path $tempDir -Recurse -Force
```
O banco ativo permanece totalmente intacto.
