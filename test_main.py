from fastapi.testclient import TestClient

from main import app

cliente = TestClient(app)


def test_crear_y_listar():
    respuesta = cliente.post(
        "/tareas",
        json={"titulo": "Estudiar FastAPI"}
    )

    assert respuesta.status_code == 201

    tarea = respuesta.json()

    assert tarea["titulo"] == "Estudiar FastAPI"
    assert tarea["hecha"] is False

    lista = cliente.get("/tareas").json()

    assert tarea in lista


def test_filtrar_tareas_hechas():
    pendiente = cliente.post(
        "/tareas",
        json={"titulo": "Tarea pendiente"}
    ).json()
    hecha = cliente.post(
        "/tareas",
        json={"titulo": "Tarea hecha", "hecha": True}
    ).json()

    respuesta = cliente.get("/tareas/filtrar?hecha=true")

    assert respuesta.status_code == 200
    tareas_filtradas = respuesta.json()
    assert hecha in tareas_filtradas
    assert pendiente not in tareas_filtradas
    assert all(tarea["hecha"] is True for tarea in tareas_filtradas)


def test_filtrar_tareas_pendientes():
    pendiente = cliente.post(
        "/tareas",
        json={"titulo": "Otra tarea pendiente"}
    ).json()
    hecha = cliente.post(
        "/tareas",
        json={"titulo": "Otra tarea hecha", "hecha": True}
    ).json()

    respuesta = cliente.get("/tareas/filtrar?hecha=false")

    assert respuesta.status_code == 200
    tareas_filtradas = respuesta.json()
    assert pendiente in tareas_filtradas
    assert hecha not in tareas_filtradas
    assert all(tarea["hecha"] is False for tarea in tareas_filtradas)


def test_obtener_tarea_existente():
    creada = cliente.post(
        "/tareas",
        json={"titulo": "Preparar evaluación", "hecha": True}
    ).json()

    respuesta = cliente.get(f"/tareas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_tarea_inexistente():
    respuesta = cliente.get("/tareas/999999")

    assert respuesta.status_code == 404


def test_marcar_tarea_como_hecha():
    creada = cliente.post(
        "/tareas",
        json={"titulo": "Revisar el proyecto"}
    ).json()

    respuesta = cliente.patch(f"/tareas/{creada['id']}/hecha")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": creada["id"],
        "titulo": "Revisar el proyecto",
        "hecha": True,
    }


def test_marcar_tarea_inexistente():
    respuesta = cliente.patch("/tareas/999999/hecha")

    assert respuesta.status_code == 404


def test_eliminar_tarea_existente():
    creada = cliente.post(
        "/tareas",
        json={"titulo": "Eliminar tarea de prueba"}
    ).json()

    respuesta = cliente.delete(f"/tareas/{creada['id']}")

    assert respuesta.status_code == 204
    tareas_restantes = cliente.get("/tareas").json()
    assert all(tarea["id"] != creada["id"] for tarea in tareas_restantes)
    tareas_eliminadas = cliente.get("/tareas/eliminadas").json()
    assert creada in tareas_eliminadas


def test_eliminar_tarea_inexistente():
    respuesta = cliente.delete("/tareas/999999")

    assert respuesta.status_code == 404


def test_listar_tareas_eliminadas():
    creada = cliente.post(
        "/tareas",
        json={"titulo": "Tarea para la papelera"}
    ).json()
    cliente.delete(f"/tareas/{creada['id']}")

    respuesta = cliente.get("/tareas/eliminadas")

    assert respuesta.status_code == 200
    assert creada in respuesta.json()


def test_recuperar_tarea_conserva_identificador():
    creada = cliente.post(
        "/tareas",
        json={"titulo": "Tarea para recuperar"}
    ).json()
    cliente.delete(f"/tareas/{creada['id']}")

    respuesta = cliente.post(
        f"/tareas/eliminadas/{creada['id']}/recuperar"
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == creada
    assert creada in cliente.get("/tareas").json()
    assert all(
        tarea["id"] != creada["id"]
        for tarea in cliente.get("/tareas/eliminadas").json()
    )


def test_recuperar_tarea_inexistente():
    respuesta = cliente.post("/tareas/eliminadas/999999/recuperar")

    assert respuesta.status_code == 404


def test_eliminar_definitivamente_tarea():
    creada = cliente.post(
        "/tareas",
        json={"titulo": "Tarea para eliminar definitivamente"}
    ).json()
    cliente.delete(f"/tareas/{creada['id']}")

    respuesta = cliente.delete(f"/tareas/eliminadas/{creada['id']}")

    assert respuesta.status_code == 204
    assert all(
        tarea["id"] != creada["id"]
        for tarea in cliente.get("/tareas/eliminadas").json()
    )


def test_eliminar_definitivamente_tarea_inexistente():
    respuesta = cliente.delete("/tareas/eliminadas/999999")

    assert respuesta.status_code == 204