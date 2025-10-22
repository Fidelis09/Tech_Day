from flask import Blueprint, render_template, request

main = Blueprint('main', __name__)

@main.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        nome = request.form.get['nome']
        email = request.form.get['email']
        return f"Nome: {nome} <br> Email: {email}"
    return render_template('form.html')