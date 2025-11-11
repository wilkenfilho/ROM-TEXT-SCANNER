# ROM Text Scanner — Ferramenta de triagem de textos em ROMs

Um utilitário em Python com interface gráfica (Tkinter) para **detectar trechos de texto legíveis** em arquivos de jogos (ROMs) — .nds, .bin, .dat, .iso, .pak, etc. Ideal para iniciar o processo de localização/tradução: identifica arquivos que contêm texto, gera dumps `.txt` automáticos e oferece amostras rápidas diretamente na interface.

---

## Principais funcionalidades

* Interface GUI em **Tkinter** com área para selecionar/arrastar pastas;
* Varredura recursiva de pastas — identifica arquivos por extensão (.nds, .bin, .dat, .iso, .pak);
* Detecta textos usando tentativas de decodificação: **UTF-8**, **Shift-JIS** e **Latin-1**;
* Suporte a **.tbl** (tabelas de mapeamento byte -> caractere) para decodificações personalizadas;
* Exporta automaticamente um arquivo `_textdump.txt` no mesmo diretório do arquivo analizado, com endereços e trechos;
* Exibe até **5 amostras** (endereço + codificação + trecho) por arquivo na interface;
* Barra de progresso e log em tempo real;
* Configuração simples e sem dependências externas (apenas Python padrão).

---

## Requisitos

* Python **3.10+** (testado com 3.10 — 3.12 deve funcionar);
* Sistema operacional: Windows / macOS / Linux;
* Nenhuma dependência externa — só `tkinter` (vem junto com a maioria das instalações do Python).

> Se `tkinter` não estiver disponível, instale-o via gerenciador de pacotes do SO (por exemplo, `sudo apt install python3-tk` no Ubuntu).

---

## Estrutura do repositório (sugerida)

```
rom-text-scanner/
├─ rom_text_scanner_gui.py     # Aplicativo principal (GUI)
├─ README.md                   # Este arquivo
├─ sample_tables/              # (opcional) exemplos de .tbl
│  └─ example.tbl
├─ .gitignore
└─ LICENSE
```

---

## Exemplo de `.tbl` (formato suportado)

O formato esperado é simples: cada linha mapeia um valor hexadecimal de byte para o caractere correspondente, no estilo:

```
00=\n
20=
41=A
42=B
80=é
```

* `00` = hexadecimal do byte (sem prefixo `0x`);
* `=` separando o hex do caractere resultante;
* O script interpreta cada byte do arquivo e substitui pelo caractere quando presente na tabela.

> Dica: salve o `.tbl` com `UTF-8`.

---

## Instalação e execução

1. Clone o repositório (ou crie um novo e adicione os arquivos):

```bash
git clone https://github.com/<seu-usuario>/rom-text-scanner.git
cd rom-text-scanner
```

2. (Opcional) crie e ative um ambiente virtual:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. Rode o aplicativo:

```bash
python rom_text_scanner_gui.py
```

4. Na janela:

* Clique em **Carregar .TBL** se quiser usar uma tabela personalizada;
* Clique na área ou use o diálogo para **selecionar uma pasta** contendo suas ROMs;
* O app varrerá os arquivos e mostrará resultados; para cada arquivo com texto será gerado `NOME_textdump.txt` no mesmo diretório.

---

## Uso via linha de comando (opcional)

Se preferir usar apenas o scanner sem GUI (script CLI pode ser adaptado), há funções no código que permitem analisar um único arquivo ou pasta. Basta invocar a função `analisar_pasta`/`analisar_rom` a partir de um pequeno wrapper CLI.

Exemplo rápido (crie `run_scan.py` que importe funções do script):

```python
from rom_text_scanner_gui import analisar_pasta, carregar_tbl
tbl = carregar_tbl('sample_tables/example.tbl')
resultados = analisar_pasta('C:/ROMs', tabela=tbl)
print(resultados)
```

---

## Formato do arquivo `_textdump.txt` gerado

Cada arquivo que tiver texto detectado gera um arquivo com conteúdo similar a:

```
Arquivo analisado: game.nds
============================================================
[0x00012AF0] (utf-8) Press Start to Begin
[0x000134E2] (utf-8) New Game / Continue
[0x000145A0] (utf-8) Loading, please wait...
...
```

* Cada linha mostra o endereço em hexadecimal, a codificação detectada e o trecho de texto.

---

## Dicas para melhorar a detecção

* **TBLs**: quando o jogo usa codificação proprietária, uma `.tbl` correta é a melhor forma de extrair strings úteis;
* **Ajustar regex**: o scanner usa uma regex simples para capturar trechos legíveis. Para capturar frases maiores ou outros alfabetos, ajuste `re` no código;
* **Tamanho mínimo**: aumente o tamanho mínimo de sequência detectada para reduzir falsos positivos (bytes aleatórios que formam palavras curtas);
* **Varredura por blocos**: em arquivos muito grandes, o código já lê em blocos — pode-se ajustar o tamanho do bloco para otimizar memória/velocidade.

---

## Limitações conhecidas

* Não é um extractor de scripts completo — o objetivo é **triagem** (dizer quais arquivos contêm texto legível);
* Sequências comprimidas/encriptadas não serão detectadas a menos que você descomprima/desencripte antes;
* O detector padrão não é linguístico (ou seja, pode retornar trechos em várias línguas se os bytes permitirem decodificação);
* Shift-JIS e UTF-8 são tentativas padrão; alguns jogos usam outras codificações e só serão legíveis com `.tbl` apropriada.

---

## Troubleshooting

* **Tkinter não abre / erro `ModuleNotFoundError: No module named 'tkinter'`**:

  * Instale o pacote do sistema (`python3-tk` em Debian/Ubuntu) ou use um Python com suporte GUI.

* **Poucos ou muitos falsos positivos**:

  * Ajuste a regex ou o tamanho mínimo de sequência;
  * Use `.tbl` quando souber que há codificação proprietária.

* **Arquivos gigantes demoram muito**:

  * Feche outros apps; aumente `bloco_tamanho` para reduzir overhead de I/O;
  * Execute em background via CLI em máquina com mais RAM.

---

## Como publicar no GitHub (passo a passo rápido)

1. Crie o repositório na sua conta (GitHub UI) com o nome `rom-text-scanner`;
2. No seu projeto local, inicialize git e faça commit:

```bash
git init
git add .
git commit -m "Initial commit: ROM Text Scanner GUI"
```

3. Conecte ao remoto criado no GitHub e envie:

```bash
git remote add origin https://github.com/<seu-usuario>/rom-text-scanner.git
git branch -M main
git push -u origin main
```

4. Adicione `README.md` (este arquivo), `LICENSE` (sugiro MIT) e `.gitignore` (ex.: `venv/`, `__pycache__/`).

---

## Sugestões de próximos passos / melhorias

* Adicionar um modo CLI robusto (argumentos, filtro por tamanho, regex customizável);
* Suporte a multi-threading para acelerar varreduras de pastas grandes;
* Exportar resultados num CSV resumido com: caminho, número de trechos, primeiro trecho, caminho do dump;
* Interface para visualizar o `_textdump.txt` dentro do app (em vez de abrir no Explorer);
* Empacotar com PyInstaller para distribuir executáveis Windows/macOS.

---

## Contribuição

Contribuições são bem-vindas: abra issues para bugs/feature requests e envie PRs com testes e descrição clara.

---

## Licença

Sugestão: **MIT License** — arquivo `LICENSE` simples e permissivo.

---

Se quiser, eu posso:

* Gerar o arquivo `LICENSE` (MIT) e `.gitignore` automaticamente;
* Criar um `run_scan.py` minimal CLI;
* Gerar o `setup.py`/`pyproject.toml` ou instruções de como empacotar com PyInstaller.

Diga qual destes você prefere que eu adicione agora.
