from locust import HttpUser, TaskSet, task, between


class CrearSolicitud(TaskSet):
    @task
    def test_carga_crear_solicitud(self):
        request = self.client.get("")
        csrftoken = request.cookies['csrftoken']
        response = self.client.post('catequista/crear/', {"nombre": "nombreTest", "apellidos": "apellidosTest", "email": "email@test.com", "disponibilidad": "disponibilidadTest", "preferencias": "preferenciasTest", "csrfmiddlewaretoken": csrftoken},
                                    headers={'Referer': self.client.base_url + 'catequista/crear/'})
        

class WebsiteUser(HttpUser):
    tasks = [CrearSolicitud]
    wait_time = between(5, 15)
