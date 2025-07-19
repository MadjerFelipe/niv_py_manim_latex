# niv_py_manin_latex

Este projeto visa simplificar e automatizar a criação de animações de equações matemáticas utilizando a biblioteca Manim. Atualmente, a geração de animações Manim a partir de equações LaTeX pode ser um processo manual e detalhado, exigindo codificação direta para cada elemento animado. Nosso objetivo é eliminar parte dessa complexidade, permitindo que os usuários:

- Extraiam equações diretamente de seus documentos LaTeX (`.tex`) existentes.

- Definam setups de animação de forma mais intuitiva e menos programática.

- Gerem vídeos Manim de suas equações com facilidade, transformando documentos estáticos em apresentações visuais dinâmicas.

A ideia central é criar uma ponte eficiente entre seus arquivos `.tex` e o poder de animação do Manim, tornando o processo acessível e ágil para educadores, estudantes e criadores de conteúdo que desejam visualizar conceitos matemáticos de forma interativa.

## Módulo `Reader`

O módulo `Reader` é a **camada de extração de dados** fundamental do projeto, responsável por localizar, validar e parsear o conteúdo de projetos LaTeX. Ele garante que as equações matemáticas possam ser identificadas e preparadas de forma estruturada para as etapas subsequentes de design e animação.

### Funcionalidades Implementadas

* **Validação e Normalização de Caminhos:** O `Reader` agora lida de forma robusta com caminhos de diretório, aceitando diferentes formatos de barras (`\` ou `/`) comuns em diversos sistemas operacionais. Ele verifica a existência e a validade do diretório fornecido, normalizando o caminho para garantir compatibilidade e evitar erros.
* **Identificação de Arquivos LaTeX:** Varrre o diretório especificado para localizar todos os arquivos com a extensão `.tex`, filtrando automaticamente os arquivos relevantes para o processamento.
* **Extração de Equações por Ambiente:** É capaz de identificar e extrair blocos completos de equações de diversos ambientes matemáticos LaTeX comumente utilizados, incluindo:
    * `\begin{equation}...\end{equation}`
    * `\begin{equation*}...\end{equation*}`
    * `\begin{eqnarray}...\end{eqnarray}`
    * `\begin{eqnarray*}...\end{eqnarray*}`
    * `\begin{align}...\end{align}`
    * `\begin{align*}...\end{align*}`
* **Granularidade de Saída Otimizada:** As equações são retornadas em um dicionário onde cada chave é um **ID único para o bloco da equação** (por exemplo, `nome_do_arquivo.tex_block_0`). O valor associado a cada ID é uma **lista de strings**, onde cada string representa uma linha daquela equação (mesmo para equações de linha única, que serão uma lista com um único item). Isso oferece a granularidade ideal para o `Designer` e `Animator` manipularem as equações como blocos ou linha por linha, conforme a necessidade de animação.
* **Tratamento de Erros de Leitura:** Inclui tratamento de exceções para lidar com problemas durante a leitura de arquivos, permitindo que o processo continue para outros arquivos mesmo se um deles estiver inacessível ou corrompido.

### Métodos Principais

* `Reader.verify_path(caminho_do_diretorio)`: Valida o `caminho_do_diretorio` fornecido, garantindo que ele exista e seja um diretório válido. Também normaliza o caminho para ser compatível com o sistema operacional.
* `Reader.get_tex_files(caminho_do_diretorio)`: Localiza todos os arquivos `.tex` dentro do `caminho_do_diretorio` validado e retorna uma lista de seus caminhos completos.
* `Reader.find_equations_in_files(tex_files)`: Percorre a lista de `tex_files` e extrai as equações de ambientes matemáticos específicos, retornando um dicionário mapeando IDs de bloco de equação para listas de strings de suas linhas.
* `Reader._find_equations_by_environment(content, begin_env, end_env)`: (Auxiliar/Interno) Função interna que utiliza expressões regulares para encontrar o conteúdo de equações dentro de um par `\begin{ambiente}...\end{ambiente}` específico em uma dada string de conteúdo.

## Designer
O módulo `Designer` será a interface de interação para a criação de cenários de animação. Sua principal função será permitir que o usuário defina como as equações, uma vez extraídas pelo Reader, devem ser visualizadas e animadas.

## Animator
O módulo `Animator` será o motor de renderização das animações, utilizando diretamente a biblioteca Manim. Ele receberá as equações processadas pelo Reader e os setups de animação definidos pelo Designer, orquestrando a criação final dos vídeos.
