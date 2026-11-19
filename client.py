import socket

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #подключаемся к серверу
HOST = "127.0.0.1"        # или IP сервера
PORT = 50007
connection.connect((HOST, PORT))

#connection.send("сообщение клиента".encode('utf8'))
try: 
    while True:
        message = input("Введите SMS: ")
        if not message:
            print('ничего не захотели вводить')
            break
        # Кодируем сообщение в байты и отправляем
        message_bytes = message.encode('utf-8')
        connection.sendall(message_bytes)

        data = connection.recv(1024)
        if not data:
            print('с сервера ничего не пришло, чао какао')
            break
        print(f'с сервера {connection} получено сообщение: {data.decode('utf8')}')
except Exception as e:
    print(f"Ошибка при отправке: {e}")
finally:
    # Закрываем соединение
    connection.close()
