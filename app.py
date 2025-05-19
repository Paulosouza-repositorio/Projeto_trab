import os
import csv
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Troque por uma chave segura

# Configurações de e-mail (GoDaddy Workspace Email)
EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_PORT = 587
EMAIL_USER = 'contato@luminusconecta.com'
EMAIL_PASSWORD = 'Luminus2023!'  # Use a senha normal do e-mail da GoDaddy


# Pasta para salvar CSVs exportados
DATA_FOLDER = os.path.join(os.path.expanduser('~'), 'luminus_data')
os.makedirs(DATA_FOLDER, exist_ok=True)

# ===================== Banco de Dados =====================

def init_db():
    with sqlite3.connect('leads.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                nome TEXT,
                email TEXT,
                telefone TEXT,
                cidade_estado TEXT,
                tem_plano TEXT,
                plano_atual TEXT,
                valor_pago TEXT,
                tipo_plano TEXT,
                tipo_pessoa TEXT,
                cpf TEXT,
                cnpj TEXT,
                mei TEXT,
                tempo_abertura TEXT,
                quantas_vidas TEXT,
                idade_vidas TEXT,
                bairro TEXT,
                interesse_novo TEXT,
                contato TEXT,
                comentario_adicional TEXT
            )
        ''')
        conn.commit()

def salvar_no_banco(dados):
    with sqlite3.connect('leads.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (
                data_hora, nome, email, telefone, cidade_estado, tem_plano,
                plano_atual, valor_pago, tipo_plano, tipo_pessoa, cpf, cnpj,
                mei, tempo_abertura, quantas_vidas, idade_vidas, bairro,
                interesse_novo, contato, comentario_adicional
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            dados.get('nome'),
            dados.get('email'),
            dados.get('telefone'),
            dados.get('cidade_estado'),
            dados.get('tem_plano'),
            dados.get('plano_atual'),
            dados.get('valor_pago'),
            dados.get('tipo_plano'),
            dados.get('tipo_pessoa'),
            dados.get('cpf'),
            dados.get('cnpj'),
            dados.get('mei'),
            dados.get('tempo_abertura'),
            dados.get('quantas_vidas'),
            dados.get('idade_vidas'),
            dados.get('bairro'),
            dados.get('interesse_novo', 'Não'),
            dados.get('contato'),
            dados.get('comentario_adicional')
        ))
        conn.commit()

# ===================== E-mail =====================

def enviar_email(dados):
    try:
        vidas = int(dados.get('quantas_vidas', '0') or 0)
        prioridade = 'ALTA PRIORIDADE' if vidas > 4 else 'Normal'

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        msg['Subject'] = f'Novo Formulário Enviado [{prioridade}]'

        body = '\n'.join([
            f"PRIORIDADE: {prioridade}",
            f"Nome: {dados.get('nome')}",
            f"E-mail: {dados.get('email')}",
            f"Telefone: {dados.get('telefone')}",
            f"Cidade/Estado: {dados.get('cidade_estado')}",
            f"Tem plano: {dados.get('tem_plano')}",
            f"Plano atual: {dados.get('plano_atual', 'Não informado')}",
            f"Valor pago atualmente: {dados.get('valor_pago', 'Não informado')}",
            f"Tipo de plano: {dados.get('tipo_plano')}",
            f"Tipo de pessoa: {dados.get('tipo_pessoa')}",
            f"CPF: {dados.get('cpf')}",
            f"CNPJ: {dados.get('cnpj')}",
            f"É MEI?: {dados.get('mei')}",
            f"Tempo de abertura: {dados.get('tempo_abertura')}",
            f"Quantas vidas: {dados.get('quantas_vidas')}",
            f"Idade das vidas: {dados.get('idade_vidas')}",
            f"Bairro: {dados.get('bairro')}",
            f"Interesse em novo plano: {dados.get('interesse_novo', 'Não')}",
            f"Autorização de contato: {dados.get('contato')}",
            f"Comentário adicional: {dados.get('comentario_adicional', 'Não informado')}"
        ])

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
            print('Email enviado com sucesso!')

    except Exception as e:
        print(f'Erro ao enviar e-mail: {str(e)}')


# ===================== Rotas =====================

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            salvar_no_banco(request.form)
            enviar_email(request.form)

            if request.form.get('plano_atual') == 'Golden Cross':
                flash('golden_cross', 'popup')

            flash('Formulário enviado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao processar dados: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('formulario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == 'admin' and request.form['senha'] == '123456':
            session['logado'] = True
            return redirect(url_for('leads'))
        else:
            flash('Credenciais inválidas!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/leads')
def leads():
    if not session.get('logado'):
        return redirect(url_for('login'))

    with sqlite3.connect('leads.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leads ORDER BY data_hora DESC')
        dados = cursor.fetchall()

    return render_template('leads.html', dados=dados)

@app.route('/exportar')
def exportar_csv():
    if not session.get('logado'):
        return redirect(url_for('login'))

    caminho_csv = os.path.join(DATA_FOLDER, 'leads_exportados.csv')
    with sqlite3.connect('leads.db') as conn, open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leads')
        colunas = [desc[0] for desc in cursor.description]
        writer = csv.writer(f)
        writer.writerow(colunas)
        writer.writerows(cursor.fetchall())

    return send_file(caminho_csv, as_attachment=True)

# ===================== Inicialização =====================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
