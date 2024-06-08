from locust import HttpUser, TaskSet, task, between


class ListarArchivos(TaskSet):

    @task
    def test_carga_listar_archivos(self):
        request = self.client.get("")
        csrftoken = request.cookies['csrftoken']
        response = self.client.post("user/login", {"email": "antoniopelaez2002@gmail.com", "password": "admin", "csrfmiddlewaretoken": csrftoken},
                                    headers={'Referer': self.client.base_url + 'user/login'})
        request2 = self.client.get("drive/listar")

class WebsiteUser(HttpUser):
    tasks = [ListarArchivos]
    wait_time = between(5, 15)
