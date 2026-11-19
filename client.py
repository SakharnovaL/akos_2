import socket

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #подключаемся к серверу
IP = "127.0.0.1"        # или IP сервера
PORT = 12333
connection.connect((IP, PORT))

data = connection.recv(1024)
print(data.decode('utf8'))

#connection.send("сообщение клиента".encode('utf8'))
try: 
    message = input("Введите SMS: ")

    # Кодируем сообщение в байты и отправляем
    message_bytes = message.encode('utf-8')

    connection.sendall(message_bytes)
except Exception as e:
    print(f"Ошибка при отправке: {e}")
finally:
    # Закрываем соединение
    connection.close()
