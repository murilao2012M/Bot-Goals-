import requests
import telebot
import time

# Configurações iniciais
url_api = "" #Apaguei a API utilizada por motivos óbvios
params = {'includes': 'league,stats,pressureStats', 'take': '3000'}
token_telegram = "" #Espaço para o seu token do telegram
chat_id = "" #Espaço para o chat id do seu telegram

# Lista para armazenar os IDs dos jogos para os quais o alerta já foi enviado
jogos_com_alerta_enviado = []

bot = telebot.TeleBot(token_telegram)

def obter_dados_jogos():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url_api, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Erro ao obter dados da API:", e)
        return None

def enviar_alerta_telegram(mensagem):
    try:
        bot.send_message(chat_id, mensagem, parse_mode='HTML')
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def analisar_jogo(jogo):
    stats = jogo.get('stats')
    pressure_stats = jogo.get('pressureStats')

    if stats is None or pressure_stats is None:
        print("Dados estatísticos não estão disponíveis para este jogo.")
        return

    home_team = jogo['homeTeam']['name']
    away_team = jogo['awayTeam']['name']
    league = jogo['league']['name']
    minute = jogo['currentTime']['minute']
    status = jogo['status']

    game_id = jogo['fixtureId']
    
    if minute is None:
        print("Minuto não está disponível para este jogo.")
        return

    shots_on_goal_home = stats.get('shotsOngoal', {}).get('home')
    shots_on_goal_away = stats.get('shotsOngoal', {}).get('away')
    dangerous_attacks_home = stats.get('dangerousAttacks', {}).get('home')
    dangerous_attacks_away = stats.get('dangerousAttacks', {}).get('away')
    
    if shots_on_goal_home is None or shots_on_goal_away is None or dangerous_attacks_home is None or dangerous_attacks_away is None:
        print("Algumas estatísticas não estão disponíveis para este jogo.")
        return

    # Inicializar os dados do jogo
    dangerous_attacks_home = stats.get('dangerousAttacks', {}).get('home', 0)
    dangerous_attacks_away = stats.get('dangerousAttacks', {}).get('away', 0)
    shots_on_goal_home = stats.get('shotsOngoal', {}).get('home', 0)
    shots_on_goal_away = stats.get('shotsOngoal', {}).get('away', 0)
    shots_off_goal_home = stats.get('shotsOffgoal', {}).get('home', 0)
    shots_off_goal_away = stats.get('shotsOffgoal', {}).get('away', 0)
    corners_home = stats.get('corners', {}).get('home', 0)
    corners_away = stats.get('corners', {}).get('away', 0)
    appm1_home = pressure_stats.get('appm1', {}).get('home', 0)
    appm1_away = pressure_stats.get('appm1', {}).get('away', 0)
    appm2_home = pressure_stats.get('appm2', {}).get('home', 0)
    appm2_away = pressure_stats.get('appm2', {}).get('away', 0)
    exg_home = pressure_stats.get('exg', {}).get('home', 0)
    exg_away = pressure_stats.get('exg', {}).get('away', 0)
    attack_momentum_home = pressure_stats.get('attack_momentum', {}).get('home', 0)
    attack_momentum_away = pressure_stats.get('attack_momentum', {}).get('away', 0)
    mh1_home = pressure_stats.get('mh1', {}).get('home', 0)
    mh1_away = pressure_stats.get('mh1', {}).get('away', 0)
    attacks_home = stats.get('attacks', {}).get('home', 0)
    attacks_away = stats.get('attacks', {}).get('away', 0)
    home_score = jogo.get('scores', {}).get('homeTeamScore', 0)
    away_score = jogo.get('scores', {}).get('awayTeamScore', 0)
    mh2_home = pressure_stats.get('mh2', {}).get('home', 0)
    mh2_away = pressure_stats.get('mh2', {}).get('away', 0)

    # Verificar se o jogo atende aos critérios para enviar o alerta
    if status.lower() == 'live' and 73 <= minute <= 80:
        criterios_atendidos = 0
        if shots_on_goal_home + shots_on_goal_away >= 10:
            criterios_atendidos += 1
        if dangerous_attacks_home + dangerous_attacks_away >= 115:
            criterios_atendidos += 1
        if shots_off_goal_home + shots_off_goal_away >= 20:
            criterios_atendidos += 1
        if attacks_home + attacks_away >= 150:
            criterios_atendidos +=1
        if home_score + away_score >= 3:
            criterios_atendidos += 1

        if criterios_atendidos >= 3:
            if game_id not in jogos_com_alerta_enviado:
                mensagem = f"<b>🔥 Jogo ao vivo:</b>\n{home_team} {home_score} x {away_score} {away_team}\n{league}\nMinuto: {minute}\n" \
                           f"<b>⚠️ Ataques Perigosos:</b> {dangerous_attacks_home} - {dangerous_attacks_away}\n" \
                           f"<b>⚠️ Ataques:</b> {attacks_home} - {attacks_away}\n" \
                           f"<b>⚽️ Chutes no Gol:</b> {shots_on_goal_home} - {shots_on_goal_away}\n" \
                           f"<b>⛔️ Chutes para Fora:</b> {shots_off_goal_home} - {shots_off_goal_away}\n" \
                           f"<b>⛳️ Escanteios:</b> {corners_home} - {corners_away}\n" \
                           f"<b>🤖 Ataques Perigosos por Minuto:</b> {appm1_home} - {appm1_away}\n" \
                           f"<b>🤖 Ataques Perigosos nos últimos 10 Minutos:</b> {appm2_home} - {appm2_away}\n" \
                           f"<b>📈 Expectativa de Gol:</b> {exg_home} - {exg_away}\n" \
                           f"<b>🚀 Momento do Ataque:</b> {attack_momentum_home} - {attack_momentum_away}\n" \
                           f"<b>📊 Momentum do Jogo (Últimos 5 Minutos):</b> {mh1_home} - {mh1_away}\n" \
                           f"<i>Por favor, faça a entrada a partir deste momento.</i>\n"
                enviar_alerta_telegram(mensagem)
                jogos_com_alerta_enviado.append(jogo['fixtureId'])

# Mensagem de início do bot
inicio_bot_mensagem = "🤖 Bot iniciado com sucesso! Aguardando novos jogos..."
enviar_alerta_telegram(inicio_bot_mensagem)

# Mensagem de início do bot
print("Bot iniciado com sucesso!")


# Loop principal
while True:
    dados_jogos = obter_dados_jogos()
    if dados_jogos:
        for jogo in dados_jogos.get('data', []):
            analisar_jogo(jogo)
    time.sleep(60)  # Intervalo entre verificações
