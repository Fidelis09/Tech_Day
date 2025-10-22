from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from storage import inicializar_banco, carregar_brinquedos, carregar_agendamentos, salvar_brinquedo, atualizar_brinquedo, deletar_brinquedo, salvar_agendamento, deletar_agendamento
from utils import formata_data

# Configurações
UPLOAD_FOLDER = 'static/imagens'
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicializa banco
inicializar_banco()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    brinquedos = carregar_brinquedos()
    return render_template('index.html', brinquedos=brinquedos)

@app.route('/agendar', methods=['GET','POST'])
def agendar():
    if request.method=='POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        dia = int(request.form['dia'])
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        inicio = int(request.form['inicio'])
        fim = int(request.form['fim'])
        ids = request.form.getlist('brinquedo')
        brinquedos = [b for b in carregar_brinquedos() if str(b.id) in ids]
        valor_total = sum(b.preco for b in brinquedos)
        salvar_agendamento(nome,telefone,dia,mes,ano,inicio,fim,','.join(ids),valor_total)
        return redirect(url_for('agendamentos'))
    brinquedos = carregar_brinquedos()
    return render_template('agendar.html', brinquedos=brinquedos)

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method=='POST':
        # cadastro ou edição
        id_ = request.form.get('id')
        nome = request.form['nome']
        tamanho = request.form['tamanho']
        preco = float(request.form['preco'])
        faixa = request.form['faixa']
        file = request.files.get('imagem')
        img_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_path = filename
        if id_:
            atualizar_brinquedo(int(id_),nome,tamanho,preco,faixa,img_path)
        else:
            salvar_brinquedo(nome,tamanho,preco,faixa,img_path)
        return redirect(url_for('admin'))
    brinquedos = carregar_brinquedos()
    return render_template('admin.html', brinquedos=brinquedos)

@app.route('/admin/delete/<int:id>')
def admin_delete(id):
    deletar_brinquedo(id)
    return redirect(url_for('admin'))

@app.route('/agendamentos')
def agendamentos():
    ags = carregar_agendamentos()
    return render_template('agendamentos.html', agendamentos=ags)

@app.route('/agendamentos/delete/<int:id>')
def agendamentos_delete(id):
    deletar_agendamento(id)
    return redirect(url_for('agendamentos'))

if __name__=='__main__':
    app.run(debug=True)