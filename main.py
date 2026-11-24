from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI(title="API de tareas")


class TareaNueva(BaseModel):
    titulo: str
    hecha: bool = False


class Tarea(TareaNueva):
    id: int


tareas: dict[int, Tarea] = {}
tareas_eliminadas: dict[int, Tarea] = {}
siguiente_id = 1


@app.get("/tareas")
def listar() -> list[Tarea]:
    return list(tareas.values())


@app.get("/tareas/eliminadas")
def listar_eliminadas() -> list[Tarea]:
    return list(tareas_eliminadas.values())


@app.get("/tareas/filtrar")
def filtrar(hecha: bool) -> list[Tarea]:
    return [tarea for tarea in tareas.values() if tarea.hecha == hecha]


@app.get("/tareas/{identificador}")
def obtener(identificador: int) -> Tarea:
    tarea = tareas.get(identificador)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@app.patch("/tareas/{identificador}/hecha")
def marcar_como_hecha(identificador: int) -> Tarea:
    tarea = tareas.get(identificador)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea.hecha = True
    return tarea


@app.delete("/tareas/{identificador}", status_code=204)
def eliminar(identificador: int) -> Response:
    tarea = tareas.pop(identificador, None)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tareas_eliminadas[identificador] = tarea
    return Response(status_code=204)


@app.post("/tareas/eliminadas/{identificador}/recuperar")
def recuperar(identificador: int) -> Tarea:
    tarea = tareas_eliminadas.pop(identificador, None)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada en la papelera")
    tareas[identificador] = tarea
    return tarea


@app.delete("/tareas/eliminadas/{identificador}", status_code=204)
def eliminar_definitivamente(identificador: int) -> Response:
    tareas_eliminadas.pop(identificador, None)
    return Response(status_code=204)


@app.post("/tareas", status_code=201)
def crear(datos: TareaNueva) -> Tarea:
    global siguiente_id
    tarea = Tarea(id=siguiente_id, **datos.model_dump())
    tareas[tarea.id] = tarea
    siguiente_id += 1
    return tarea