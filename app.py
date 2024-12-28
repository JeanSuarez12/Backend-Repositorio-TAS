from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests  # Importa la biblioteca para realizar solicitudes HTTP

app = Flask(__name__)
CORS(app)  # Habilita solicitudes CORS desde cualquier origen

# Datos en memoria
tasks = {}  # Diccionario para almacenar tareas
comments = {}  # Diccionario para almacenar comentarios por tarea

# Generadores de ID
task_id_counter = 1
comment_id_counter = 1

# Ruta para crear una nueva tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id_counter
    data = request.get_json()

    title = data.get('title')
    description = data.get('description', "")
    assigned_to = data.get('assigned_to')

    if not title or not assigned_to:
        return jsonify({"error": "Campos obligatorios: title y assigned_to"}), 400

    # Crear la tarea
    task = {
        "id": task_id_counter,
        "title": title,
        "description": description,
        "assigned_to": assigned_to,
        "status": "pending"
    }
    tasks[task_id_counter] = task
    task_id_counter += 1

    # Enviar notificación al microservicio
    try:
        notify_response = requests.post(
            'http://127.0.0.1:5001/notify',  # URL del microservicio de notificaciones
            json={
                "email": assigned_to,  # Usa el valor de 'assigned_to' como email
                "message": f"Se te ha asignado una nueva tarea: {title}"
            }
        )
        # Verificar si la solicitud fue exitosa
        if notify_response.status_code != 200:
            print(f"Error al enviar notificación: {notify_response.text}")
    except Exception as e:
        print(f"Error al conectarse al microservicio de notificaciones: {str(e)}")

    return jsonify(task), 201

# Ruta para obtener todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(list(tasks.values())), 200

# Ruta para agregar un comentario a una tarea
@app.route('/tasks/<int:task_id>/comments', methods=['POST'])
def add_comment(task_id):
    global comment_id_counter
    data = request.get_json()

    user = data.get('user')
    comment = data.get('comment')

    if not user or not comment:
        return jsonify({"error": "Campos obligatorios: user y comment"}), 400

    if task_id not in tasks:
        return jsonify({"error": "Tarea no encontrada"}), 404

    comment_data = {
        "id": comment_id_counter,
        "task_id": task_id,
        "user": user,
        "comment": comment,
        "timestamp": datetime.utcnow().isoformat()
    }
    if task_id not in comments:
        comments[task_id] = []
    comments[task_id].append(comment_data)
    comment_id_counter += 1

    return jsonify(comment_data), 201

# Ruta para obtener todos los comentarios de una tarea
@app.route('/tasks/<int:task_id>/comments', methods=['GET'])
def get_comments(task_id):
    if task_id not in tasks:
        return jsonify({"error": "Tarea no encontrada"}), 404

    return jsonify(comments.get(task_id, [])), 200

#Nueva ruta para actualizar el estado de una tarea 
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    assigned_to = data.get('assigned_to')
    status = data.get('status')

    if task_id not in tasks:
        return jsonify({"error": "Tarea no encontrada"}), 404

    if title:
        tasks[task_id]['title'] = title
    if description:
        tasks[task_id]['description'] = description
    if assigned_to:
        tasks[task_id]['assigned_to'] = assigned_to
    if status:
        tasks[task_id]['status'] = status

    return jsonify(tasks[task_id]), 200


#Eliminar Tarea
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id not in tasks:
        return jsonify({"error": "Tarea no encontrada"}), 404

    del tasks[task_id]
    if task_id in comments:
        del comments[task_id]  # También elimina los comentarios relacionados
    return jsonify({"message": "Tarea eliminada"}), 200

if __name__ == '__main__':
    app.run(debug=True)
