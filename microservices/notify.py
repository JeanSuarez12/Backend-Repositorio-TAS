from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita solicitudes CORS desde cualquier origen

# Ruta para notificaciones
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()

    email = data.get('email')
    message = data.get('message')

    # Validar que los campos obligatorios estén presentes
    if not email or not message:
        return jsonify({"error": "Campos obligatorios: email y message"}), 400

    # Simular envío de correo imprimiendo en consola
    print(f"Enviando correo a {email} con el mensaje: {message}")

    return jsonify({"message": "Notificación enviada correctamente"}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)