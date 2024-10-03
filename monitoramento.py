import os
import time
import pyodbc
import win32gui
from pynput import mouse, keyboard
from datetime import datetime

# Pega o nome do login do usuário no computador
usuario = os.getlogin()

# Defina o nome da janela que você deseja monitorar
janela_nome = "(Remoto)"  # Nome parcial da janela que você quer monitorar

# Inicializa a variável tempo_atividade
tempo_atividade = 0  # Variável para guardar o tempo total de atividade (em segundos)

# Configurações de conexão com o SQL Server
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=tcon_john.sqlserver.dbaas.com.br;"  # Troque pelo nome ou IP do servidor
    "DATABASE=tcon_john;"  # Troque pelo nome do seu banco
    "UID=tcon_john;"  # Troque pelo seu usuário
    "PWD=32412744;"  # Troque pela sua senha
)

# Função para conectar ao banco de dados
def conectar_ao_banco():
    while True:
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            print("Conexão com o banco de dados estabelecida.")
            return conn, cursor
        except pyodbc.Error as e:
            print(f"Erro de conexão com o banco de dados: {e}. Tentando novamente em 5 segundos...")
            time.sleep(5)  # Espera 5 segundos antes de tentar reconectar

# Função para inserir/atualizar o tempo de atividade no banco de dados
def atualizar_tempo_no_banco(tempo_atividade, conn, cursor):
    try:
        # Captura a hora atual
        hora_atual = datetime.now().time()
        data_atual = datetime.now().strftime('%Y-%m-%d')

        # Definir a coluna correta com base no período do dia
        if hora_atual >= datetime.strptime('06:00:00', '%H:%M:%S').time() and hora_atual <= datetime.strptime('12:00:00', '%H:%M:%S').time():
            # Período da manhã
            cursor.execute('''
            IF EXISTS (SELECT 1 FROM HorasTrabalhadas WHERE Usuario = ? AND Data = ?)
            BEGIN
                UPDATE HorasTrabalhadas
                SET TempodeAtividade = TempodeAtividade + ?, SegundosManha = ISNULL(SegundosManha, 0) + ?
                WHERE Usuario = ? AND Data = ?
            END
            ELSE
            BEGIN
                INSERT INTO HorasTrabalhadas (Usuario, Data, Processo, TempodeAtividade, SegundosManha)
                VALUES (?, ?, ?, ?, ?)
            END
            ''', (usuario, data_atual, tempo_atividade, tempo_atividade, usuario, data_atual,
                  usuario, data_atual, janela_nome, tempo_atividade, tempo_atividade))
        
        elif hora_atual > datetime.strptime('12:00:00', '%H:%M:%S').time() and hora_atual <= datetime.strptime('18:00:00', '%H:%M:%S').time():
            # Período da tarde
            cursor.execute('''
            IF EXISTS (SELECT 1 FROM HorasTrabalhadas WHERE Usuario = ? AND Data = ?)
            BEGIN
                UPDATE HorasTrabalhadas
                SET TempodeAtividade = TempodeAtividade + ?, SegundosTarde = ISNULL(SegundosTarde, 0) + ?
                WHERE Usuario = ? AND Data = ?
            END
            ELSE
            BEGIN
                INSERT INTO HorasTrabalhadas (Usuario, Data, Processo, TempodeAtividade, SegundosTarde)
                VALUES (?, ?, ?, ?, ?)
            END
            ''', (usuario, data_atual, tempo_atividade, tempo_atividade, usuario, data_atual,
                  usuario, data_atual, janela_nome, tempo_atividade, tempo_atividade))
        
        elif hora_atual > datetime.strptime('18:00:00', '%H:%M:%S').time() and hora_atual <= datetime.strptime('23:59:59', '%H:%M:%S').time():
            # Período da noite
            cursor.execute('''
            IF EXISTS (SELECT 1 FROM HorasTrabalhadas WHERE Usuario = ? AND Data = ?)
            BEGIN
                UPDATE HorasTrabalhadas
                SET TempodeAtividade = TempodeAtividade + ?, SegundosNoite = ISNULL(SegundosNoite, 0) + ?
                WHERE Usuario = ? AND Data = ?
            END
            ELSE
            BEGIN
                INSERT INTO HorasTrabalhadas (Usuario, Data, Processo, TempodeAtividade, SegundosNoite)
                VALUES (?, ?, ?, ?, ?)
            END
            ''', (usuario, data_atual, tempo_atividade, tempo_atividade, usuario, data_atual,
                  usuario, data_atual, janela_nome, tempo_atividade, tempo_atividade))

        conn.commit()
        print("Dados inseridos ou atualizados com sucesso!")
    except pyodbc.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}. Tentando novamente em 5 segundos...")
        time.sleep(5)  # Espera 5 segundos antes de tentar novamente

# Função pra pegar o título da janela ativa
def get_janela_ativa():
    try:
        janela = win32gui.GetForegroundWindow()
        titulo_janela = win32gui.GetWindowText(janela)
        return titulo_janela
    except Exception as e:
        print(f"Erro ao pegar a janela ativa: {e}")
        return ""

# Função pra verificar se a janela ativa contém "Visual Rodopar" no título
def janela_ativa():
    try:
        titulo_janela = get_janela_ativa()
        if janela_nome.lower() in titulo_janela.lower():
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar janela ativa: {e}")
        return False

# Função pra monitorar a atividade do mouse e teclado
def monitorar_atividade():
    global tempo_atividade  # Tornando a variável global acessível dentro da função
    ativo = False

    # Conecta ao banco de dados
    conn, cursor = conectar_ao_banco()

    # Função que vai ser chamada sempre que houver movimento/click no mouse ou teclas pressionadas
    def on_any_activity(*args):
        nonlocal ativo
        ativo = True

    # Listeners para mouse e teclado
    try:
        mouse_listener = mouse.Listener(on_move=on_any_activity, on_click=on_any_activity)
        keyboard_listener = keyboard.Listener(on_press=on_any_activity)

        mouse_listener.start()
        keyboard_listener.start()

        try:
            while True:
                if janela_ativa():
                    ativo = False
                    # Espera 1 segundo para registrar a atividade
                    time.sleep(1)
                    if ativo:
                        tempo_atividade += 1
                        print(f"Janela '{janela_nome}' ativa. Tempo de atividade: {tempo_atividade} segundos")

                    # Atualiza o banco de dados a cada ciclo (1 segundo)
                    atualizar_tempo_no_banco(tempo_atividade, conn, cursor)

                    # Zera o tempo de atividade para o próximo ciclo
                    tempo_atividade = 0
                else:
                    print(f"Janela '{janela_nome}' não encontrada ou não está ativa.")
                    time.sleep(2)

        except KeyboardInterrupt:
            print("Monitoramento encerrado.")
        finally:
            # Para os listeners quando o loop for interrompido
            mouse_listener.stop()
            keyboard_listener.stop()

    except Exception as e:
        print(f"Erro ao iniciar os listeners: {e}")

   
if __name__ == "__main__":
    try:
        monitorar_atividade()
    except Exception as e:
        print(f"Erro geral no monitoramento: {e}")
