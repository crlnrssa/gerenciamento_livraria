Sistema de Gerenciamento de Livraria

VIDEO EXECUÇÃO: https://drive.google.com/drive/folders/11TRmXB31Wa5YoMbJPTZ3XEcOkm-Qmoc3?usp=sharing

Este é um sistema para gerenciar uma coleção de livros em uma livraria. O projeto foi desenvolvido em Python e utiliza SQLite para o armazenamento de dados. Ele permite operações básicas de CRUD (Criar, Ler, Atualizar, Deletar), além de funcionalidades para importação, exportação, backup e geração de relatórios.

Funcionalidades
- Adicionar, Exibir, Atualizar e Remover livros do banco de dados.
- Buscar livros por autor.
- Backup Automático: Cria uma cópia de segurança do banco de dados antes de qualquer alteração (adição, atualização ou remoção).
- Limpeza de Backups: Mantém apenas os 5 backups mais recentes, excluindo os mais antigos automaticamente.
- Exportação de Dados: Exporta a lista completa de livros para um arquivo no formato .csv.
- Importação de Dados: Importa uma lista de livros a partir de um arquivo .csv.
- Geração de Relatórios: Cria relatórios da lista de livros nos formatos .html e .pdf.

Pré-requisitos
- Python 3.6 ou superior.
- A biblioteca reportlab para a geração de relatórios em PDF.

Instalação
- Clone este repositório ou baixe os arquivos.
- Para a funcionalidade de gerar relatórios em PDF, instale a dependência necessária: pip install reportlab
  
Como Usar
- Abra um terminal ou prompt de comando.
- Navegue até o diretório onde o arquivo livraria.py está localizado.
- Execute o script com o seguinte comando: python livraria.py
- O programa exibirá um menu com as opções disponíveis. Basta digitar o número da opção desejada e pressionar Enter.

O script criará automaticamente a seguinte estrutura de diretórios para organizar os arquivos:

|-- livraria.py        # O script principal do sistema
|-- /data/             # Armazena o banco de dados (livraria.db)
|-- /backups/          # Salva as cópias de segurança do banco de dados
|-- /exports/          # Local onde relatórios (CSV, HTML, PDF) são salvos
