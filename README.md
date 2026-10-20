# bibliaco-dados

Dados da [Bíblia Colaborativa](https://github.com/joathanmf/bibliaco) que são grandes demais para o repositório do app.
Os arquivos ficam nos **Releases**; o app guarda só o endereço e o `sha256` de cada um (manifesto) e o importador
confere o `sha256` antes de importar.

## Comentários clássicos (`classicos/`)

Originais em inglês, em **domínio público**, obtidos da [Free Use Bible API](https://bible.helloao.org) (AO Lab) em
2026-10-19. Licença declarada pela fonte para todas as obras abaixo:
[Public Domain Mark 1.0](https://creativecommons.org/publicdomain/mark/1.0/). Release:
[`classicos-en-2026-10-19`](https://github.com/joathanmf/bibliaco-dados/releases/tag/classicos-en-2026-10-19).

| Obra | Autor | Título | Anos | Trechos | Palavras | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| `matthew-henry` | Matthew Henry | Commentary on the Whole Bible | 1706-1721 | 5.343 | 6.097.530 | 11.4 MB |
| `john-gill` | John Gill | Exposition of the Old and New Testaments | 1746-1763 | 29.773 | 8.596.399 | 15.8 MB |
| `adam-clarke` | Adam Clarke | Commentary and Critical Notes on the Holy Bible | 1810-1826 | 14.205 | 2.566.597 | 5.2 MB |
| `jamieson-fausset-brown` | Robert Jamieson, A. R. Fausset, David Brown | Commentary Critical and Explanatory on the Whole Bible | 1871 | 18.299 | 1.999.744 | 4.3 MB |
| `keil-delitzsch` | Carl Friedrich Keil, Franz Delitzsch | Biblical Commentary on the Old Testament | 1857-1878 | 6.946 | 4.206.898 | 8.7 MB |
| `john-calvin` | João Calvino (John Calvin) | Calvin's Commentaries (tradução inglesa da Calvin Translation Society) | 1844-1856 | 7.316 | 8.369.341 | 16.3 MB |

As traduções para o português serão feitas pelo projeto e publicadas como `<obra>.pt-BR.jsonl.gz`, no mesmo formato,
apontando para as mesmas chaves.

### Formato

`<obra>.<idioma>.jsonl.gz`: JSON Lines compactado, uma linha por trecho, em ordem bíblica:

```json
{"key": "JHN.3.1", "book": "JHN", "chapter": 3, "start_verse": 1, "end_verse": 21, "text": "We found, in the close..."}
```

- `key`: chave estável do trecho (`LIVRO.capítulo.versículo inicial`), igual em todos os idiomas. É ela que liga a
  tradução ao original.
- `book`: código USFM do livro. `chapter` 0 é a introdução do livro; `start_verse` 0 é a introdução do capítulo.
- `end_verse`: o comentário vem por seção, não por versículo. O trecho vai do `start_verse` até o versículo anterior
  ao próximo trecho (ou até o fim do capítulo, pela versificação da KJV).
- `text`: texto puro, parágrafos separados por linha em branco.
- O `.gz` é gerado com `mtime=0`: o mesmo conteúdo dá sempre o mesmo `sha256`.

`manifest.en.json` traz, por obra: autor, título, anos, licença, fonte, data da coleta, `sha256` da fonte e do arquivo,
contagens e o que foi ignorado.

### O que foi ignorado (falhas da fonte)

- `matthew-henry`: ISA 67: capítulo ausente na fonte; ISA 68: capítulo fora do cânon, com texto
- `jamieson-fausset-brown`: PSA 146: capítulo ausente na fonte; MRK 15: capítulo ausente na fonte
- `keil-delitzsch`: EXO 37: capítulo ausente na fonte; EXO 38: capítulo ausente na fonte; NUM 17: capítulo ausente na fonte; JOB 25: capítulo ausente na fonte; PSA 101: capítulo ausente na fonte; PSA 117: capítulo ausente na fonte; PSA 131: capítulo ausente na fonte; PSA 133: capítulo ausente na fonte; EZK 4: capítulo ausente na fonte; EZK 5: capítulo ausente na fonte; EZK 36: capítulo ausente na fonte; DAN 6:29: versículo fora do cânon
- `john-calvin`: GEN 33:21: versículo fora do cânon; LEV 12: capítulo ausente na fonte

### Como regerar

`tools/build_classicos.py` monta os arquivos a partir do JSON baixado da API (um diretório por obra, com
`books.json` e `<LIVRO>_<capítulo>.json`) e do `db/canon.yml` do app:

```bash
python3 -I tools/build_classicos.py RAW_DIR caminho/para/bibliaco/db/canon.yml OUT_DIR 2026-10-19
```
