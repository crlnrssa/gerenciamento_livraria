import os
import sqlite3
import csv
from pathlib import Path
from datetime import datetime
import shutil

# Tenta importar a biblioteca para gerar PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

# Obtém o caminho do diretório atual do script
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
EXPORTS_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "livraria.db"

# Funções de inicialização e backup 
def inicializar_diretorios():
    # Cria os diretórios de dados, backups e exports se eles não existirem
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)

def conectar_db():
    # Conecta no banco de dados e cria a tabela de livros se ela não existir
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER,
            preco REAL
        )
    ''')
    conn.commit()
    return conn

def fazer_backup():
    # Cria o backup do banco de dados na pasta de backups
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = BACKUP_DIR / f"backup_livraria_{agora}.db"
    try:
        shutil.copyfile(DB_PATH, backup_path)
        print(f"Backup do banco de dados criado em: {backup_path}")
    except FileNotFoundError:
        print("Erro: Não foi possível fazer o backup. O arquivo do banco de dados não foi encontrado.")

def limpar_backups():
    # Deixa somente os 5 primeiros backups e exclui os mais antigos
    backups = sorted(BACKUP_DIR.glob("backup_livraria_*.db"), key=os.path.getmtime, reverse=True)
    if len(backups) > 5:
        for backup_antigo in backups[5:]:
            os.remove(backup_antigo)
            print(f"Backup antigo removido: {backup_antigo}")

def adicionar_livro():
    # Adiciona um livro no banco de dados
    fazer_backup() # Backup antes da modificação
    
    # Validação para garantir que os campos de texto não fiquem vazios
    while True:
        titulo = input("Título do livro: ")
        if titulo.strip():
            break
        print("O título não pode ser vazio.")
    
    while True:
        autor = input("Autor: ")
        if autor.strip():
            break
        print("O autor não pode ser vazio.")
    
    # Validação para ano e preço
    while True:
        try:
            ano_str = input("Ano de publicação: ")
            ano = int(ano_str)
            if len(ano_str) == 4:
                break
            else:
                print("Ano inválido. Por favor, insira um ano com 4 dígitos.")
        except ValueError:
            print("Entrada inválida. O ano deve ser um número inteiro.")
            
    while True:
        try:
            preco = float(input("Preço: "))
            if preco >= 0:
                break
            else:
                print("O preço não pode ser negativo.")
        except ValueError:
            print("Entrada inválida. O preço deve ser um número decimal (use '.' como separador).")

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)", (titulo, autor, ano, preco))
    conn.commit()
    conn.close()
    print("Livro adicionado com sucesso!")

def exibir_livros():
    # Mostra todos os livros 
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    conn.close()

    if not livros:
        print("Nenhum livro cadastrado.")
        return

    print("\n--- Livros Cadastrados ---")
    for livro in livros:
        print(f"ID: {livro[0]} | Título: {livro[1]} | Autor: {livro[2]} | Ano: {livro[3]} | Preço: R${livro[4]:.2f}")
    print("--------------------------")
    return livros # Retorna os livros para uso nos relatórios

def atualizar_preco():
    # Atualiza o preço do livro
    exibir_livros()
    try:
        livro_id = int(input("ID do livro para atualizar o preço: "))
        novo_preco = float(input("Novo preço: "))
        if novo_preco < 0:
            print("O preço não pode ser negativo.")
            return
    except ValueError:
        print("Entrada inválida. O ID e o preço devem ser números.")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros WHERE id=?", (livro_id,))
    if cursor.fetchone():
        fazer_backup() # Backup antes da modificação
        cursor.execute("UPDATE livros SET preco=? WHERE id=?", (novo_preco, livro_id))
        conn.commit()
        print(f"Preço do livro com ID {livro_id} atualizado com sucesso!")
    else:
        print("Livro não encontrado.")
    conn.close()

def remover_livro():
    # Apaga um livro 
    exibir_livros()
    try:
        livro_id = int(input("ID do livro para remover: "))
    except ValueError:
        print("Entrada inválida. O ID deve ser um número.")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros WHERE id=?", (livro_id,))
    if cursor.fetchone():
        fazer_backup() # Backup antes da modificação
        cursor.execute("DELETE FROM livros WHERE id=?", (livro_id,))
        conn.commit()
        print(f"Livro com ID {livro_id} removido com sucesso!")
    else:
        print("Livro não encontrado.")
    conn.close()

def buscar_por_autor():
    # Busco o livro pelo nome no autor
    autor_busca = input("Nome do autor para buscar: ")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros WHERE autor LIKE ?", (f'%{autor_busca}%',))
    livros = cursor.fetchall()
    conn.close()

    if not livros:
        print(f"Nenhum livro encontrado para o autor '{autor_busca}'.")
        return

    print(f"\n--- Livros do Autor '{autor_busca}' ---")
    for livro in livros:
        print(f"Título: {livro[1]} | Ano: {livro[3]} | Preço: R${livro[4]:.2f}")
    print("------------------------------------------")

def exportar_para_csv():
    # Exporta todos os livros para um arquivo CSV
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, autor, ano_publicacao, preco FROM livros")
    livros = cursor.fetchall()
    conn.close()

    if not livros:
        print("Nenhum livro para exportar.")
        return

    csv_path = EXPORTS_DIR / "livros_exportados.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["titulo", "autor", "ano_publicacao", "preco"]) 
        writer.writerows(livros)

    print(f"Dados exportados com sucesso para: {csv_path}")

def importar_de_csv():
    # Insere os livros de um CSV no banco de dados
    csv_path = input(f"Informe o caminho do arquivo CSV (ex: {EXPORTS_DIR / 'livros.csv'}): ")
    if not os.path.exists(csv_path):
        print("Erro: O arquivo não foi encontrado.")
        return

    fazer_backup() # Backup antes da modificação
    conn = conectar_db()
    cursor = conn.cursor()
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
            try:
                titulo, autor, ano, preco = row
                cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)", (titulo, autor, int(ano), float(preco)))
            except (ValueError, IndexError):
                print(f"Linha ignorada devido a formato incorreto: {row}")
                continue

    conn.commit()
    conn.close()
    print("Dados importados com sucesso!")

def gerar_relatorio():
    # Função para gerar relatórios em diferentes formatos
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, autor, ano_publicacao, preco FROM livros")
    livros = cursor.fetchall()
    conn.close()

    if not livros:
        print("Não há livros cadastrados para gerar um relatório.")
        return

    print("\n--- Geração de Relatório ---")
    print("Escolha o formato:")
    print("1. HTML")
    print("2. PDF")
    
    opcao = input("Opção: ")
    
    if opcao == '1':
        gerar_relatorio_html(livros)
    elif opcao == '2':
        gerar_relatorio_pdf(livros)
    else:
        print("Opção inválida.")

def gerar_relatorio_html(livros):
    # Gera um relatório em formato HTML 
    html_path = EXPORTS_DIR / "relatorio_livros.html"
    
    # Conteúdo do HTML
    html_content = f"""
    <html>
    <head>
        <title>Relatório de Livros da Livraria</title>
        <style>
            body {{ font-family: sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            th {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Livros</h1>
        <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        <table>
            <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Autor</th>
                <th>Ano</th>
                <th>Preço</th>
            </tr>
    """
    
    for livro in livros:
        html_content += f"""
            <tr>
                <td>{livro[0]}</td>
                <td>{livro[1]}</td>
                <td>{livro[2]}</td>
                <td>{livro[3]}</td>
                <td>R$ {livro[4]:.2f}</td>
            </tr>
        """
        
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
        
    print(f"Relatório HTML gerado com sucesso em: {html_path}")

def gerar_relatorio_pdf(livros):
    # Gera um relatório em formato PDF 
    if not REPORTLAB_DISPONIVEL:
        print("\nERRO: A biblioteca 'reportlab' é necessária para gerar PDFs.")
        print("Por favor, instale-a usando o comando: pip install reportlab")
        return

    pdf_path = EXPORTS_DIR / "relatorio_livros.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    elements.append(Paragraph("Relatório de Livros da Livraria", styles['h1']))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    
    # Dados da tabela 
    data = [["ID", "Título", "Autor", "Ano", "Preço"]]
    for livro in livros:
        preco_formatado = f"R$ {livro[4]:.2f}"
        data.append([livro[0], livro[1], livro[2], livro[3], preco_formatado])
        
    # Estilo da tabela
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)
    
    print(f"Relatório PDF gerado com sucesso em: {pdf_path}")


def main():
    inicializar_diretorios()
    conectar_db().close()  

    while True:
        print("\n--- Sistema de Gerenciamento de Livraria ---")
        print("1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Gerar relatório (HTML/PDF)")
        print("10. Sair") 

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_livro()
            limpar_backups()
        elif opcao == '2':
            exibir_livros()
        elif opcao == '3':
            atualizar_preco()
            limpar_backups()
        elif opcao == '4':
            remover_livro()
            limpar_backups()
        elif opcao == '5':
            buscar_por_autor()
        elif opcao == '6':
            exportar_para_csv()
        elif opcao == '7':
            importar_de_csv()
            limpar_backups()
        elif opcao == '8':
            fazer_backup()
            limpar_backups()
        elif opcao == '9': 
            gerar_relatorio()
        elif opcao == '10': 
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()