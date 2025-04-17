import os
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, send_file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Altere para um valor seguro

# Caminho para salvar os arquivos CSV
CSV_FILE = "clientes_goldencross.csv"

# Função para salvar os dados em um arquivo CSV
def salvar_dados_csv(dados):
    # Verificar se o arquivo CSV já existe
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Se o arquivo não existir, escrever o cabeçalho
        if not file_exists:
            writer.writerow(["Nome", "E-mail", "Telefone", "Cidade/Estado", "Tempo de Permanência", 
                             "Motivo da Saída", "Data de Saída", "Contato", "Comentário Adicional", "Arquivo"])
        
        # Escrever os dados
        writer.writerow(dados)

# Rota principal - Formulário
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Capturando os dados do formulário
            nome = request.form["nome"]
            email = request.form["email"]
            telefone = request.form["telefone"]
            cidade_estado = request.form["cidade_estado"]
            tempo_permanencia = request.form["tempo_permanencia"]
            motivo_saida = request.form["motivo_saida"]
            data_saida = request.form["data_saida"]
            contato = request.form["contato"]
            comentario_adicional = request.form["comentario_adicional"]
            arquivo = request.files["arquivo"]

            # Criando a lista de dados a serem salvos no CSV
            dados = [nome, email, telefone, cidade_estado, tempo_permanencia, motivo_saida, data_saida, contato, comentario_adicional, arquivo.filename if arquivo else ""]

            # Salvando os dados no arquivo CSV
            salvar_dados_csv(dados)

            flash("Reclamação enviada com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erro ao enviar dados: {e}", "danger")
            return redirect(url_for("index"))

    return render_template("form.html")

# Rota para visualizar os dados
@app.route("/dados")
def dados():
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        leitor = csv.reader(f)
        dados = list(leitor)
    return render_template("dados.html", dados=dados)

# Rota para download do CSV
@app.route("/download")
def download():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)



