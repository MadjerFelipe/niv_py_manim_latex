# niv_py_manin_latex

Este projeto visa simplificar e automatizar a criação de animações de equações matemáticas utilizando a biblioteca Manim. Atualmente, a geração de animações Manim a partir de equações LaTeX pode ser um processo manual e detalhado, exigindo codificação direta para cada elemento animado. Nosso objetivo é eliminar parte dessa complexidade, permitindo que os usuários:

- Extraiam equações diretamente de seus documentos LaTeX (`.tex`) existentes.

- Definam setups de animação de forma mais intuitiva e menos programática.

- Gerem vídeos Manim de suas equações com facilidade, transformando documentos estáticos em apresentações visuais dinâmicas.

A ideia central é criar uma ponte eficiente entre seus arquivos `.tex` e o poder de animação do Manim, tornando o processo acessível e ágil para educadores, estudantes e criadores de conteúdo que desejam visualizar conceitos matemáticos de forma interativa.

## Reader

O módulo `Reader` é a camada de extração de dados do projeto, responsável por localizar, validar e parsear o conteúdo de projetos LaTeX. Ele garante que as equações matemáticas possam ser identificadas e preparadas para as etapas subsequentes de design e animação. Utilize este módulo para centralizar a lógica de leitura e pré-processamento dos arquivos que serão utilizados nas animações ou demais funcionalidades do projeto. Suas funcionalidades incluem:

- Leitura de arquivos de entrada e conversão de conteúdo em estruturas utilizáveis pelo restante do projeto.
- Manipulação de strings e tratamento de comandos LaTeX, se necessário.
- Possível suporte a diferentes formatos de entrada, com tratamento de erros e validação de dados.

### Métodos Principais
`Reader.verify_path(caminho_do_diretorio)`
    Este método é o primeiro ponto de contato com o sistema de arquivos. Ele valida o caminho fornecido, garantindo que ele realmente existe e aponta para um diretório. Se o caminho for inválido ou não for um diretório, o programa é encerrado para evitar erros nas etapas posteriores.

`Reader.get_tex_files(caminho_do_diretorio)`
    Após a validação do diretório, esta função é responsável por localizar todos os arquivos .tex dentro do caminho especificado. Ela retorna uma lista de caminhos completos para esses arquivos. Caso nenhum arquivo .tex seja encontrado no diretório, o processo é interrompido, pois não haveria equações para processar.

`Reader.find_equations_in_files(tex_files)`
    Este é o coração da funcionalidade de extração do Reader. Ele recebe a lista de arquivos .tex e, para cada um, lê seu conteúdo para identificar e extrair equações matemáticas.

Ele busca especificamente o conteúdo dentro dos seguintes ambientes LaTeX, que são comumente usados para equações:

- `\begin{equation}...\end{equation}`

- `\begin{equation*}...\end{equation*}`

- `\begin{eqnarray}...\end{eqnarray}`

- `\begin{eqnarray*}...\end{eqnarray*}`

- `\begin{align}...\end{align}`

- `\begin{align*}...\end{align*}`

As equações extraídas são armazenadas em um dicionário, onde a chave é o nome do arquivo .tex (por exemplo, meu_documento.tex) e o valor é uma lista de strings, cada string contendo o LaTeX de uma equação encontrada naquele arquivo.

## Designer
O módulo `Designer` será a interface de interação para a criação de cenários de animação. Sua principal função será permitir que o usuário defina como as equações, uma vez extraídas pelo Reader, devem ser visualizadas e animadas.

## Animator
O módulo `Animator` será o motor de renderização das animações, utilizando diretamente a biblioteca Manim. Ele receberá as equações processadas pelo Reader e os setups de animação definidos pelo Designer, orquestrando a criação final dos vídeos.
