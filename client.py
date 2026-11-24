import socket

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                              #подключаемся к серверу, AF_INET передаем все через протокол IPv4, SOCK_STREAM через протокол TCP
HOST = "127.0.0.1"                                                                          #или IP сервера
PORT = 50007
connection.connect((HOST, PORT))                                                            #соединяемся с сервером

#connection.send("сообщение клиента".encode('utf8'))
try: 
    while True:
        outgoing_message = input("Введите SMS: ")
        if not outgoing_message:                                                            #если реально ничего не ввели, клиент отключается от сервера
            print('ничего не захотели вводить')
            break
        if outgoing_message.lower().strip() == 'ping':                                      
            message_bytes = outgoing_message.encode('utf-8')                                #кодируем сообщение в байты и отправляем
        else:                                                                               #если ввели не ping, отправляем сообщение, что вы глупенький, и выпадаем в ошибку
            message_bytes = 'stupid man'.encode('utf-8')
        connection.sendall(message_bytes)                                                   #sendall() отправит точно все сообщение
        income_message = connection.recv(1024)                                              #усыпляем клиента в ожидании ответа от сервера
        if not income_message:                                                              #сервер не прислал ответ и отключил клиента от себя
            print('с сервера ничего не пришло, чао какао')
            break
        if income_message.decode('utf8').lower().strip() == 'pong':      
            print(f'с сервера получено сообщение: {income_message.decode('utf8')}')
        else:                                                                               #если вернулось не pong, тк мы отправили не ping, то ошибка
            raise ValueError(f'неожиданный ответ от сервера, "{income_message.decode('utf8')}", ожидалось pong')
except Exception as e:
    print(f"Ошибка при отправке: {e}")
finally:
    connection.close()                                                                      #закрываем соединение