import socket

dis_port = 55555                                                                                #общий порт для автоматического поиска сервера в сети

def find_server(timeout=3.0):
    upd_sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                  #создаем неблокирующий upd сокет, чтоб клиент мог находить наш сервер
    upd_sok.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                               #SO_BROADCAST широковещательная рассылка
    upd_sok.settimeout(timeout)                                                                 #если через 3 секунды нам никто не ответит, ошибка времени ожидания
    try:
        mes = 'who_server'.encode('utf-8')                                                      #кодируем сообщение
        upd_sok.sendto(mes, ("255.255.255.255", dis_port))                                      #отправляем его по широковещательному адресу, чтоб серевр его точно увидел
        while True:
            data, ser_adr = upd_sok.recvfrom(1024)                                              #замораживаем клиента пока сервер нам не ответит
            mess = data.decode('utf-8').strip()
            if mess.startswith('i_server'):                                                     #если нам реально ответил сервер
                tcp_port = int(mess.split(':')[1])
                server_ip = ser_adr[0]
                return server_ip, tcp_port
    except socket.timeout:                                                                      #если долго ждем ответ
        raise RuntimeError('сервер не найден. убедитесь, что server.py запущен и устройства находятся в одной сети')
    finally:
        upd_sok.close()

def run_client():
    host, port = find_server()
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((host, port))
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

if __name__ == "__main__":
    try:
        run_client()
    except Exception as err:
        print(f"Не удалось запустить клиент: {err}")