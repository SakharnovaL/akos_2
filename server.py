#много клиентов и серверов как работают, в какой очередности и что делать вообще хз
#два клиента без сервера чд
import socket

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
IP = "0.0.0.0"      # слушаем все интерфейсы
PORT = 12333
listener.bind((IP, PORT))
listener.listen(0)

print("Сервер запущен, ждём клиента...")
connection, address = listener.accept()
print(f"Подключен клиент: {address}")

connection.send("Привет, подключайся!".encode('utf8'))

# читаем, пока клиент не закроет соединение
while True:
    data = connection.recv(1024)

    if not data:
        print("клиент ничего не отправил")
        break

    message = data.decode('utf-8').strip()
    print(f'сообщение от клиента: {message}')

    if message == "Привет, сервер":
        print("Привет, клиент!")
    else:
        print('Я хз кто ты')
    #print("сообщение сервера", data.decode("utf8"))

connection.close()
listener.close()