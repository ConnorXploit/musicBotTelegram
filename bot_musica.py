import telebot, os
import urllib.request
from bs4 import BeautifulSoup

bot = telebot.TeleBot(os.environ['API_BOT'])

@bot.message_handler(commands=['start', 'help'])
def saludar(message):
	bot.reply_to(message, 'Hola! Que tal? Que puedo hacer por ti?')

def getVideosLink(busqueda):
	query = urllib.parse.quote(busqueda)

	url = "https://www.youtube.com/results?search_query={q}".format(q=query)

	response = urllib.request.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')

	videos = [ 'https://www.youtube.com{q}'.format(q=vid['href']) for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}) ]

	return videos

def getWeleleContent(busqueda):
	query = urllib.parse.quote(busqueda)

	url = "https://welele.es/tagged/{q}".format(q=query)

	response = urllib.request.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')

	images = [ im.find('img')['href'] for im in [art.findAll('img') for art in soup.findAll('article') ] ]

	return images

@bot.message_handler(commands=['welele'])
def welele(message):
	buscar = message.text.split('welele')[1].strip()
	if buscar:
		busqueda = buscar.split('[')[0].strip()
		try:
			max_resultados = int(buscar.split('[')[1].strip().split(']')[0])
		except:
			max_resultados = 10

		resultados = getWeleleContent(busqueda)

		resultados = resultados[0:max_resultados] 

		for res in resultados:
			bot.reply_to(message, res)
	else:
		bot.reply_to(message, 'Debes decirme algo para que busque')

@bot.message_handler(commands=['musica'])
def musica(message):
	buscar = message.text.split('musica')[1].strip()
	if buscar:
		busqueda = buscar.split('[')[0].strip()
		try:
			max_videos = int(buscar.split('[')[1].strip().split(']')[0])
		except:
			max_videos = 10

		videos = getVideosLink(busqueda)

		videos = videos[0:max_videos] 

		for v in videos:
			bot.reply_to(message, v)
	else:
		bot.reply_to(message, 'Debes decirme algo para que busque')

bot.polling()
