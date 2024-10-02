import os
import time
import pyodbc
import win32gui
from pynput import mouse, keyboard
from datetime import datetime

# Pega o nome do login do usuário no computador
usuario = os.getlogin()

# Configurações de conexão com o SQL Server
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER= ADRESS;"  # Troque pelo nome ou IP do servidor
    "DATABASE= BASE;"  # Troque pelo nome do seu banco
    "UID= USER;"  # Troque pelo seu usuário
    "PWD= PASSWORD;"  # Troque pela sua senha
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Variável pra guardar o tempo total de atividade (por segundo)
tempo_atividade = 0
janela_nome = "EXEMPLO"  # Nome parcial da janela que você quer monitorar

# Função pra pegar o título da janela ativa
def get_janela_ativa():
    janela = win32gui.GetForegroundWindow()
    titulo_janela = win32gui.GetWindowText(janela)
    return titulo_janela

# Função pra verificar se a janela ativa contém "EXEMPLO" no título
def janela_ativa():
    titulo_janela = get_janela_ativa()
    if janela_nome.lower() in titulo_janela.lower():
        return True
    return False

# Função para inserir/atualizar o tempo de atividade no banco de dados
def atualizar_tempo_no_banco(tempo_atividade):
    data_atual = datetime.now().strftime('%Y-%m-%d')

# A query primeiro verifica se ja existe um registro no dia, se ja existir ele apenas da um update (soma), caso nao tenha, ele cria o registro e faz o processo anterior ate o fim do dia
    cursor.execute('''
    IF EXISTS (SELECT 1 FROM HorasProcessos WHERE Usuario = ? AND Data = ?)
    BEGIN
    UPDATE HorasProcessos
    SET TempodeAtividade = TempodeAtividade + ?
    WHERE Usuario = ? AND Data = ?
    END
    ELSE
    BEGIN
    INSERT INTO HorasProcessos (Usuario, Data, Processo, TempodeAtividade)
    VALUES (?, ?, ?, ?)
    END
    ''', (usuario, data_atual, tempo_atividade, usuario, data_atual, 
          usuario, data_atual, janela_nome, tempo_atividade))

    conn.commit()

# Função pra monitorar a atividade do mouse e teclado
def monitorar_atividade():
    global tempo_atividade
    ativo = False

    # Função que vai ser chamada sempre que houver movimento/click no mouse ou teclas pressionadas
    def on_any_activity(*args):
        nonlocal ativo
        ativo = True

    # Listeners para mouse e teclado
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
                atualizar_tempo_no_banco(tempo_atividade)

                # Zera o tempo de atividade para o próximo ciclo
                tempo_atividade = 0
            else:
                print(f"Janela '{janela_nome}' não encontrada ou não está ativa.")
                time.sleep(5)

    except KeyboardInterrupt:
        print("Monitoramento encerrado.")
    finally:
        # Para os listeners quando o loop for interrompido
        mouse_listener.stop()
        keyboard_listener.stop()

   
if __name__ == "__main__":
    monitorar_atividade()

    # Fecha a conexão com o banco de dados
    conn.close()
