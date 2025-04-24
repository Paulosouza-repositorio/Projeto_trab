import os
import csv
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Caminho onde os dados serão salvos
DATA_FOLDER = os.path.join(os.path.expanduser('~'), 'luminus_data')
os.makedirs(DATA_FOLDER, exist_ok=True)

# Configurações do Gmail
EMAIL_REMETENTE = 'pcbsouza@id.uff.br'
EMAIL_DESTINO = 'paulu2009@hotmail.com'
EMAIL_SENHA = 'kqqa sjmd zvlr qcsu'

def salvar_dados_no_seu_pc(dados):
    """Salva os dados localmente"""
    filename = f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(DATA_FOLDER, filename)

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

def enviar_email_avisando(dados):
    """Envia um e-mail de aviso com os dados"""
    msg = EmailMessage()
    msg['Subject'] = '📩 Novo formulário enviado!'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO

    corpo = f"""
Novo formulário recebido!

Nome: {dados['nome']}
Email: {dados['email']}
Telefone: {dados['telefone']}
Cidade/Estado: {dados['cidade_estado']}
Tem plano: {dados.get('tem_plano', 'não')}
Plano atual: {dados.get('plano_atual', '')}
Tipo do plano: {dados.get('tipo_plano', '')}
Interesse em novo plano: {dados.get('interesse_novo', 'não')}
Autoriza contato: {dados.get('contato', 'Não')}
Comentário adicional: {dados.get('comentario_adicional', '')}
"""
    msg.set_content(corpo)

    # Envia com SMTP do Gmail
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_REMETENTE, EMAIL_SENHA)
        smtp.send_message(msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            salvar_dados_no_seu_pc(request.form)
            enviar_email_avisando(request.form)

            if request.form.get('plano_atual') == 'Golden Cross':
                flash('golden_cross', 'popup')

            flash('Formulário enviado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao processar formulário: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)

