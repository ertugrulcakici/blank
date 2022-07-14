from socket import socket


class Victim:
    def __init__(self,client: socket, victim_type: str, name: str):

        self.client = client
        self.is_alive = True
        self.name = name
        self.victim_type = victim_type

    def send_data(self, data) -> bool:
        try:
            if not isinstance(data, bytes):
                data = str(data).encode()
        except Exception as e:
            print("send_data datası dönüştürülemedi: "+str(e))
            return False
        try:
            self.client.sendall(data)
            return True
        except Exception as e:
            print("cliente data gönderilemedi: "+str(e))
            self.is_alive = False
            return False

    def check_alive(self) -> bool:
        if self.is_alive:
            try:
                self.client.sendall(b'')
                self.is_alive = True
                return True
            except Exception as e:
                self.is_alive = False
                return False
        else:
            return False
        
    def get_connection_data(self) -> tuple:
        return {"client_ip": self.client.getsockname()[0], "client_port": self.client.getsockname()[1]}

    def __str__(self) -> str:
        return "Victim info: "+str(self.get_connection_data())+"\tVictim: "+self.name+":"+self.victim_type

    def close(self) -> None:
        try:
            self.client.close()
        except: pass
        self.is_alive = False
