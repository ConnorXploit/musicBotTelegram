import telebot, os
import urllib.request
from bs4 import BeautifulSoup
from io import BytesIO
PUBLICAR_ID = '1115946057'

bot = telebot.TeleBot(os.environ['API_BOT'])

HELP_MSG = """/start - Inicia el Servidor de musica
/help - Muestra este mensaje de ayuda
/musica - Tienes que pasar un nombre de artista o cancion y te dará maxímo 10 links por defecto (Puedes pasar un parametro para ampliar o minimizar la respuesta [4] por ejemplo)
/welele - Devuelve contenido de welele buscando por tags como puede ser "Humor", "Risa", "Videos", "Gatos", etc. (Puedes pasar un parametro para ampliar o minimizar la respuesta [40] por ejemplo)

Ejemplos:

/welele gatos [11]
/musica iron maiden [3]
/musica rap"""

@bot.message_handler(commands=['start'])
def saludar(message):
	bot.reply_to(message, 'Hola! Que tal? Que puedo hacer por ti?')

@bot.message_handler(commands=['help'])
def saludar(message):
	bot.reply_to(message, HELP_MSG)

def getVideosLink(busqueda):
	query = urllib.parse.quote(busqueda)

	url = "https://www.youtube.com/results?search_query={q}".format(q=query)

	response = urllib.request.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')

	videos = [ 'https://www.youtube.com{q}'.format(q=vid['href']) for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}) ]

	return videos

def getWeleleContent(busqueda, max_resultados):
	data = []
	query = urllib.parse.quote(busqueda)

	url = "https://welele.es/tagged/{q}".format(q=query)

	response = urllib.request.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')

	images = [ im['src'] for im in soup.find('div', { 'class' : 'posts' }).findAll('img') ]

	videos = [ im['src'] for im in soup.find('div', { 'class' : 'posts' }).findAll('source') ]
	
	data = images + videos
	if len(data) < max_resultados:
		pages = int(max_resultados/len(data))
		for page in range(2, pages):
			url = "https://welele.es/tagged/{q}/page/{n}".format(q=query, n=page)
			response = urllib.request.urlopen(url)
			html = response.read()
			soup = BeautifulSoup(html, 'html.parser')

			images = [ im['src'] for im in soup.find('div', { 'class' : 'posts' }).findAll('img') ]

			videos = [ im['src'] for im in soup.find('div', { 'class' : 'posts' }).findAll('source') ]
			data += images + videos
	return data

@bot.message_handler(commands=['welele'])
def welele(message):
	buscar = message.text.split('welele')[1].strip().replace('PUBLICAR', '')
	if buscar:
		busqueda = buscar.split('[')[0].strip()
		try:
			max_resultados = int(buscar.split('[')[1].strip().split(']')[0])
		except:
			max_resultados = 10

		publicar = True if 'PUBLICAR' in message.text.split('welele')[1].strip() else False

		resultados = getWeleleContent(busqueda, max_resultados)

		resultados = resultados[0:max_resultados] 

		for res in resultados:
			try:
				if res.split('.')[-1] in ('jpg', 'png'):
					img = BytesIO(urllib.request.urlopen(res).read())
					bot.send_chat_action(message.chat.id, 'upload_photo')
					bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
					if publicar:
						bot.send_chat_action(PUBLICAR_ID, 'upload_photo')
						bot.send_photo(PUBLICAR_ID, img)
				elif res.split('.')[-1] in ('mp4', 'mpg', 'mpeg', 'avi', 'mkv', 'gif', 'gifv'):
					video = BytesIO(urllib.request.urlopen(res).read())
					bot.send_chat_action(message.chat.id, 'upload_video')
					bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
					if publicar:
						bot.send_chat_action(PUBLICAR_ID, 'upload_video')
						bot.send_video(PUBLICAR_ID, video)
				else:
					bot.reply_to(message, res)
					if publicar:
						bot.reply_to(PUBLICAR_ID, res)
			except:
				pass
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
