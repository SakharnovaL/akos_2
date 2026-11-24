import socket

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                  #подключаемся к серверу, AF_INET передаем все через протокол IPv4, SOCK_STREAM через протокол TCP
HOST = "127.0.0.1"                                                              #или IP сервера
PORT = 50007
connection.connect((HOST, PORT))                                                #соединяемся с сервером

#connection.send("сообщение клиента".encode('utf8'))
try: 
    while True:
        message = input("Введите SMS: ")
        if not message:                                                         #если реально ничего не ввели, клиент отключается от сервера
            print('ничего не захотели вводить')
            break
        message_bytes = message.encode('utf-8')                                 #кодируем сообщение в байты и отправляем
        connection.sendall(message_bytes)                                       #sendall() отправит точно все сообщение
        data = connection.recv(1024)                                            #усыпляем клиента в ожидании ответа от сервера
        if not data:                                                            #сервер не прислал ответ и отключил клиента от себя
            print('с сервера ничего не пришло, чао какао')
            break
        print(f'с сервера получено сообщение: {data.decode('utf8')}')
except Exception as e:
    print(f"Ошибка при отправке: {e}")
finally:
    connection.close()                                                          #закрываем соединение