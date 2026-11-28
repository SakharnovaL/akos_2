import socket
import threading                                                                                #для создания параллельных потоков

dis_port = range(55555, 55565)                                                                  #для одновременной работы сразу нескольких серверов
p2p_port = range(55566, 55576)                                                                  #для болталки клиентов без сервера

def find_server(timeout=3.0):
    upd_sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                  #создаем неблокирующий upd сокет, чтоб клиент мог находить наш сервер
    upd_sok.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                               #SO_BROADCAST широковещательная рассылка
    upd_sok.settimeout(timeout)                                                                 #если через 3 секунды нам никто не ответит, ошибка времени ожидания
    servers = []                                                                                #список серверов, доступных для подключения
    try:
        mes = 'who_server'.encode('utf-8')                                                      #кодируем сообщение
        for port in dis_port:                                                                   #отправляем сообщение сразу на все 10 портов
            try:
                upd_sok.sendto(mes, ("255.255.255.255", port))                                  #отправляем его по широковещательному адресу, чтоб серевр его точно увидел
            except OSError:
                pass
        while True:
            try:
                data, ser_adr = upd_sok.recvfrom(1024)                                          #замораживаем клиента пока сервер нам не ответит
                mess = data.decode('utf-8').strip()
                if mess.startswith('i_server'):                                                 #если нам реально ответил сервер
                    tcp_port = int(mess.split(':')[1])
                    server_ip = ser_adr[0]
                    servers.append((server_ip, tcp_port))                                       #добавляем в список найденый сервер
            except socket.timeout:                                                              #если долго ждем ответ
                break 
        if not servers:
            raise RuntimeError('сервер не найден. убедитесь, что server.py запущен и устройства находятся в одной сети')
        elif len(servers) == 1:
            return servers[0]
        else:
            servers.sort()
            print('найдено несколько серверов:')
            for ind, (ip, port) in enumerate(servers, start=1):
                print(f'{ind}. {ip}:{port}')
            choise = int(input('выберите сервер: ')) - 1
            return servers[choise]
    finally:
        upd_sok.close()

#режим работы 1: общение клиента с сервром
def run_ping_mode():
    host, port = find_server()
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((host, port))
    try: 
        connection.sendall('mode:ping'.encode('utf-8'))                                         #отправляем сообщение с выбранным режимом
        if connection.recv(1024) != b'ready':                                                   #если с сервера не пришло сообщение ready, то обрубаем все
            raise RuntimeError('сервер не подтвердил режим работы')
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

#режим работы 2: общение клиентов друг с другом через сервер
def receive_from_server(connection):                                                            #печатает входящии сообщения с сервера, не мешая нам вводить свои
    while True:
        try:
            income_mes = connection.recv(1024)
            if not income_mes:                                                                  #проверяет не прислаи нам пустую строчку, что является сигналом закрытия сервера
                print('сервер закрыл соединение')
                break
            print(f'\r{income_mes.decode("utf-8").strip()}\nвы: ', end='')                      #печатает пришедшее от собеседников сообщение. \r cдвигаем каретку в начало строки, тем самым затирая вы:, чтоб был красивый вывод
        except OSError:
            break

def run_server_chat_mode():
    host, port = find_server()
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((host, port))
    try:
        connection.sendall('mode:chat'.encode('utf-8'))                                         #отправляем сообщение с выбранным режимом
        if connection.recv(1024) != b'ready':                                                   #если с сервера не пришло сообщение ready, то обрубаем все
            raise RuntimeError('сервер не подтвердил режим работы')
        print(f'вы вошли в общий чат через сервер ({host}:{port}). пустая строка - выход из чата')
        threading.Thread(target=receive_from_server, args=(connection,), daemon=True).start()   #этот монстр запускает функцию receive_from_server в фоновом потоке, чтоб мы могли как писать сообщения. та ки принимать сообщения с сервера. threading.Thread создает объект нового фонового потока, target показывает конкретно какую функцию надо выполнять, args передет аргументы в функцию, daemon деалет поток фоновым
        while True:
            outgoing_mes = input('вы: ')
            if not outgoing_mes:                                                                #если оставим стороку пустой - выход
                print('выход из чата')
                break
            connection.sendall(outgoing_mes.encode('utf-8'))
    finally:
        connection.close()

#режим работы 3: общение клиентов друг с другом без сервера
def listen_p2p(sock, my_port):                                                                  #полчаем сообщения от других клиентов
    while True:
        try:
            data, adr = sock.recvfrom(1024)
            if adr[1] != my_port:                                                               #если не свое сообщение
                income_mes = data.decode('utf-8')
                if income_mes:
                    print(f'\r{adr[1]}: {income_mes.strip()}\nвы: ', end='')
        except ConnectionResetError:                                                            #чтоб на винде все нормальн работало, тк она когда видит неподключенные порты сразу в ошибку выпадает
            continue
        except OSError:
            break

def p2p_boardcats(sock, my_port, mes):                                                          #вывод красивого сообщения на экран, чтоб много раз одно и тоже не писать
    mes_bytes = mes.encode('utf-8')
    for port in p2p_port:
        if port != my_port:
            try:
                sock.sendto(mes_bytes, ("255.255.255.255", port))
            except OSError:
                pass

def run_p2p_chat_mode():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                     #подключаемся через интернет и udp порт
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                                  #разрешаем оправлять на широковещательные пакеты
    my_port = None
    for port in p2p_port:
        try:
            sock.bind(("0.0.0.0", port))                                                        #пытаемся занять порт
            my_port = port
            break
        except OSError:
            continue
    if my_port is None:
        sock.close()
        raise RuntimeError('порты (55566 - 55576) заняты')
    print(f'чат без сервера. ваш порт: {my_port}. Enter или пустая строка выход из чата')
    threading.Thread(target=listen_p2p, args=(sock, my_port), daemon=True).start()              #этот монстр запускает функцию receive_from_server в фоновом потоке, чтоб мы могли как писать сообщения. та ки принимать сообщения с сервера. threading.Thread создает объект нового фонового потока, target показывает конкретно какую функцию надо выполнять, args передет аргументы в функцию, daemon деалет поток фоновым
    p2p_boardcats(sock, my_port, 'присоединился к чату')
    try:
        while True:
            outgoing_mes = input('вы: ')
            if not outgoing_mes:                                                                #если оставим стороку пустой - выход
                print('выход из чата')
                break
            p2p_boardcats(sock, my_port, outgoing_mes)
    finally:
        p2p_boardcats(sock, my_port, 'покинул чат')
        sock.close()

if __name__ == "__main__":
    try:
        while True:
            print('выберите режим работы')
            print('0. завершить работу клиента')
            print('1. общение клиента с сервером')
            print('2. общение клиента с другими клиентами через сервер')
            print('3. общение клиента с другими клиентами без сервера')
            mode = input('ваш выбор: ').strip()
            if mode == '0':
                break
            elif mode == '1':
                run_ping_mode()
            elif mode == '2':
                run_server_chat_mode()
            elif mode == '3':
                run_p2p_chat_mode()
            else:
                print('режима под таким номером не существует. попробуйте еще раз')
    except KeyboardInterrupt:
        print('программа завершена')
    except Exception as err:
        print(f"Не удалось запустить клиент: {err}")