import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Troque por uma chave segura

# Configuração para enviar e-mail
EMAIL_HOST = 'pcbsouza@id.uff.br'  # Para Gmail
EMAIL_PORT = 587
EMAIL_USER = 'paulu2009@hotmail.com'  # Seu e-mail
EMAIL_PASSWORD = 'kqqa sjmd zvlr qcsu'  # Senha do aplicativo (não a senha normal do Gmail)

# Pasta para salvar os arquivos CSV
DATA_FOLDER = os.path.join(os.path.expanduser('~'), 'luminus_data')
os.makedirs(DATA_FOLDER, exist_ok=True)

def enviar_email(dados):
    """Função para enviar email com os dados do formulário."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        msg['Subject'] = 'Novo Formulário Enviado'

        body = f"""
        Dados do formulário:
        Nome: {dados['nome']}
        E-mail: {dados['email']}
        Telefone: {dados['telefone']}
        Cidade/Estado: {dados['cidade_estado']}
        Tem plano: {dados['tem_plano']}
        Plano atual: {dados.get('plano_atual', 'Não informado')}
        Tipo de plano: {dados['tipo_plano']}
        Interesse em novo plano: {dados.get('interesse_novo', 'Não')}
        Autorização de contato: {dados['contato']}
        Comentário adicional: {dados.get('comentario_adicional', 'Não informado')}
        """

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
            print('Email enviado com sucesso!')
    
    except Exception as e:
        print(f'Erro ao enviar e-mail: {str(e)}')

def salvar_dados_no_seu_pc(dados):
    """Salva os dados no seu computador (servidor)"""
    filename = f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(DATA_FOLDER, filename)

    # Verifica se o arquivo já existe para não sobrescrever
    counter = 1
    while os.path.exists(filepath):
        filename = f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{counter}.csv"
        filepath = os.path.join(DATA_FOLDER, filename)
        counter += 1

    # Escreve os dados no arquivo CSV
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Data_Hora', 'Nome', 'Email', 'Telefone', 'Cidade_Estado',
            'Tem_Plano', 'Plano_Atual', 'Tipo_Plano', 'Interesse_Novo_Plano',
            'Autoriza_Contato', 'Comentarios'
        ])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            dados['nome'],
            dados['email'],
            dados['telefone'],
            dados['cidade_estado'],
            dados.get('tem_plano', 'não'),
            dados.get('plano_atual', ''),
            dados.get('tipo_plano', ''),
            dados.get('interesse_novo', 'não'),
            dados.get('contato', 'Não'),
            dados.get('comentario_adicional', '')
        ])

    return filepath

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Salva os dados no SEU computador
            caminho_arquivo = salvar_dados_no_seu_pc(request.form)
            print(f"Arquivo salvo com sucesso em: {caminho_arquivo}")

            # Envia o e-mail com os dados
            enviar_email(request.form)

            # Verifica se é Golden Cross para mostrar o popup
            if request.form.get('plano_atual') == 'Golden Cross':
                flash('golden_cross', 'popup')

            flash('Formulário enviado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao salvar dados ou enviar e-mail: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)
