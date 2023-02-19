import requests as req
from html.parser import HTMLParser
from html.entities import name2codepoint
import unittest
import time
import zipfile
from io import BytesIO
import os
import re

from tkinter import filedialog
from tkinter import *


#----------------------------------------------------------------------------------------------------

def get_sub_id_from_href(s):
	re_res = re.search(r"\/subtitles\/\d+\/", s)
	sub_id = None
	if re_res:
		return re_res[0].split('/')[-2]

class TestGetSubIdFromHref(unittest.TestCase):

	def test_get(self):
		text = '/en/subtitles/8343327/ted-lasso-two-aces-pb'
		res = get_sub_id_from_href(text)
		
		self.assertEqual(res, '8343327')
#----------------------------------------------------------------------------------------------------

def get_se_and_ep_from_filename(s):
	re_res = re.search(r"S\d{1,3}E\d{1,3}", s)
	se_and_ep = None
	if re_res:
		se_and_ep = re_res[0]
		se, ep = se_and_ep.replace('S', '').split('E')
		return int(se), int(ep), se_and_ep

class TestGetSeAndEpFromFilename(unittest.TestCase):

	def test_get(self):
		text = "Ted.Lasso.S01E05.REPACK.720p.ATVP.WEBRip.x264-GalaxyTV.mkv"
		res = get_se_and_ep_from_filename(text)
		
		self.assertEqual(res, (1,5, 'S01E05'))
#----------------------------------------------------------------------------------------------------
def parse_reLink(s):
	return s.split('reLink(')[1].replace(' ', '').split("'")[1]

class TestParseReLink(unittest.TestCase):

	def test_reLink(self):
		text = "if (!window.__cfRLUnblockHandlers) return false; reLink(event,'/en/search/sublanguageid-pob/idmovie-957535')"
		res = parse_reLink(text)
		self.assertEqual(res, '/en/search/sublanguageid-pob/idmovie-957535')
#----------------------------------------------------------------------------------------------------
class ParseList(HTMLParser):
	def __init__(self, link_has_str):
		super(ParseList, self).__init__()
		self.link_has_str = link_has_str
		self.res = []
		self.se_and_ep = None
		self._onclick = None

	def handle_starttag(self, tag, attrs):		
		attrs_dict = dict((k, v) for k,v in attrs)
		if tag in ['a', 'td', 'tr'] and 'onclick' in attrs_dict and 'reLink' in attrs_dict['onclick'] and self.link_has_str in attrs_dict['onclick']:
			#print(attrs_dict)
			# print(attrs_dict['onclick'])
			self._onclick = attrs_dict['onclick']

	def handle_data(self, data):
		if self._onclick != None:
			if data.strip().startswith('[S') and data.strip().endswith(']') and 'E' in data:
				href = parse_reLink(self._onclick)
				#print(self._onclick)
				self.res.append({'href': href, 'se_and_ep': data.strip()})
				self._onclick = None


class TestParseList(unittest.TestCase):

	def test_get_links(self):
		text = '''<table id="search_results"><tbody><tr style="background:#d8d8d8;" class="head"><th colspan="2" title="" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/en/search2/sublanguageid-pob/moviename-ted+lasso/sort-0/asc-1'">Movie name</th><th class="head" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/en/search2/sublanguageid-pob/moviename-ted+lasso/sort-1/asc-0'"><img alt="Movie rating" width="16" height="16" src="//static.opensubtitles.org/gfx/icons/imdb_small.gif" title="Movie rating"></th><th class="head" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/en/search2/sublanguageid-pob/moviename-ted+lasso/sort-3/asc-0'">#</th><th class="head" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/en/search2/sublanguageid-pob/moviename-ted+lasso/sort-2/asc-0'">Latest</th></tr><tr id="name957535" class="change even" onclick="if (!window.__cfRLUnblockHandlers) return false; reLink(event,'/en/search/sublanguageid-pob/idmovie-957535')"><td style="width:2%;margin:0px;padding:0px;text-align:center;"><img style="margin:0px;padding:0px;" width="43" height="63" src="//static8.opensubtitles.org/gfx/thumbs/0/9/4/6/11046490.jpg"></td><td style="width:80%" id="main957535"><strong><a class="bnone" title="subtitles - &quot;Ted Lasso&quot; Two Aces" href="/en/search/sublanguageid-pob/idmovie-957535">"Ted Lasso" Two Aces(2020)</a></strong>[S01E06]<br><a rel="nofollow" onclick="if (!window.__cfRLUnblockHandlers) return false; rdr(this);" class="p a a_1" href="/en/DkuDANbGFrgmoEH2X/EVqpd70shdm72d2m0Y6BAgIAE" title="&quot;Ted Lasso&quot; Two Aces - Watch online">Watch online</a><a style="margin-left:7px" class="p a a_2" onclick="if (!window.__cfRLUnblockHandlers) return false; rdr(this);" href="https://www.opensubtitles.website/" title="Download Subtitles Player">Download Subtitles Player</a></td><td align="center"><a onclick="if (!window.__cfRLUnblockHandlers) return false; reLink(event,'/redirect/http://www.imdb.com/title/tt11046490/');" title="4695 (votes)" href="/redirect/http://www.imdb.com/title/tt11046490/">8.5</a></td><td>2</td><td><abbr class="timeago" title="2020-09-08T00:00:00+02:00">08/09/2020</abbr></td></tr><tr style="height:115px;text-align:center;margin:0px;padding:0px;background-color:#DFEBF9;"><td colspan="5"> <iframe id="a9e951a7" name="a9e951a7" src="https://ads1.opensubtitles.org/1/www/delivery/afr.php?zoneid=5&amp;cb=694310&amp;query=Ted+Lasso+Two+Aces" frameborder="0" scrolling="no" width="728" height="140" pta1gu9km=""><a href='http://ads1.opensubtitles.org/1/www/delivery/ck.php?n=a72d3ec6&amp;cb=694310&amp;query=Ted+Lasso+Two+Aces' target='_blank'><img src='http://ads1.opensubtitles.org/1/www/delivery/avw.php?zoneid=5&amp;cb=694310&amp;n=a72d3ec6&amp;query=Ted+Lasso+Two+Aces' border='0' alt='' /></a></iframe></td></tr><tr id="name957534" class="change even" onclick="if (!window.__cfRLUnblockHandlers) return false; reLink(event,'/en/search/sublanguageid-pob/idmovie-957534')"><td style="width:2%;margin:0px;padding:0px;text-align:center;"><img style="margin:0px;padding:0px;" width="43" height="63" src="//static9.opensubtitles.org/gfx/thumbs/0/6/1/4/11044160.jpg"></td><td style="width:80%" id="main957534"><strong><a class="bnone" title="subtitles - &quot;Ted Lasso&quot; Tan Lines" href="/en/search/sublanguageid-pob/idmovie-957534">"Ted Lasso" Tan Lines(2020)</a></strong>[S01E05]<br><a rel="nofollow" onclick="if (!window.__cfRLUnblockHandlers) return false; rdr(this);" class="p a a_1" href="/en/LXcXVZINjj3cEeUADJtua/WrizdwYlaZdPRXgu6U56c" title="&quot;Ted Lasso&quot; Lavender - Watch online">Watch online</a><a style="margin-left:7px" class="p a a_2" onclick="if (!window.__cfRLUnblockHandlers) return false; rdr(this);" href="https://www.opensubtitles.website/" title="Download Subtitles Player">Download Subtitles Player</a></td><td align="center"><a onclick="if (!window.__cfRLUnblockHandlers) return false; reLink(event,'/redirect/http://www.imdb.com/title/tt14968630/');" title="4215 (votes)" href="/redirect/http://www.imdb.com/title/tt14968630/">8.0</a></td><td>1</td><td><abbr class="timeago" title="2021-07-30T00:00:00+02:00">30/07/2021</abbr></td></tr></tbody></table>'''

		parser = ParseList('/idmovie-')
		parser.feed(text)
		#print(parser.res)
		self.assertEqual(parser.res, [{'href': '/en/search/sublanguageid-pob/idmovie-957535', 'se_and_ep': '[S01E06]'}, {'href': '/en/search/sublanguageid-pob/idmovie-957534', 'se_and_ep': '[S01E05]'}])
	
#----------------------------------------------------------------------------------------------------

HEADERS={
	#"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	# "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
	# "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
	# "sec-ch-ua-mobile": "?0",
	# "sec-ch-ua-platform": "\"Linux\"",
	# "sec-fetch-dest": "document",
	# "sec-fetch-mode": "navigate",
	# "sec-fetch-site": "same-origin",
	# "sec-fetch-user": "?1",
	# "upgrade-insecure-requests": "1"	
}

def remove_file_extension(filename):
	return ".".join(filename.split(".")[:-1]).strip()

def download_file(url, movie_filename, folder_selected):
	with req.get(url, stream=True, timeout=3) as r:
		file = zipfile.ZipFile(BytesIO(r.content))
		for f in file.infolist():
			if f.filename.endswith('.srt'):
				save_as_filename = f'{remove_file_extension(movie_filename)}.srt'
				print(save_as_filename)
				f.filename = save_as_filename
				file.extractall(path=folder_selected, members=[f])
				break

def search_movie_name_with_se_and_ep(sublanguageid, q, se_and_ep_from_filename = None):
	se, ep, se_and_ep = se_and_ep_from_filename
	movie_name_before_se_and_ep = q.lower().split(se_and_ep.lower())[0].replace(".", " ").strip().replace(" ", "+").lower()
	r = req.get(f'https://www.opensubtitles.org/en/search/sublanguageid-{sublanguageid}/season-{se}/episode-{ep}/moviename-{movie_name_before_se_and_ep}', allow_redirects=True, timeout=3)
	print("Search for SE and EP: ", r.url)
	return r.url

def search_movie_name(sublanguageid, q):
	"""return list of movies"""
	q_replace = q.replace(" ", "+").replace(".", "+").lower()
	r = req.get(f'https://www.opensubtitles.org/en/search2/sublanguageid-{sublanguageid}/moviename-{q_replace}', allow_redirects=True, timeout=3)
	print("Search for movie/show", r.url)
	parser = ParseList('/idmovie-')
	parser.feed(r.text)
	return parser.res

def search_subtitles_for_idmovie(sublanguageid, idmovie):
	"""return movie id"""
	r = req.get(f'https://www.opensubtitles.org/en/search/sublanguageid-{sublanguageid}/idmovie-{idmovie}', {'headers': HEADERS}, allow_redirects=True, timeout=3)
	#print(r.url)
	#r = req.get(f'https://www.opensubtitles.org/en/search/sublanguageid-pob/idmovie-{r.url}', {'headers': HEADERS}, allow_redirects=True, timeout=3)
	parser = ParseList('/subtitles/')
	parser.feed(r.text)
	#print(parser.res)
	return parser.res[0]['href'].split('/')[-2]

def main():
	#UI
	root = Tk()
	
	OPTIONS = [
		"pob",
		"ar",
		"zh",
		"da",
		"nl",
		"en",
		"eo",
		"fi",
		"fr",
		"de",
		"el",
		"he",
		"hi",
		"ga",
		"it",
		"ja",
		"ko",
		"mn",
		"no",
		"fa",
		"pl",
		"pt",
		"ru",
		"es",
		"sv",
		"th",
		"ur",
		"vi",
		"cy",
		"yi",
		"zu",
		"id"
    ]

	variable = StringVar(root)
	variable.set(OPTIONS[0])

	w = OptionMenu(root, variable, *OPTIONS)
	w.pack()

	def ok():
		sublanguageid = variable.get()
		folder_selected = filedialog.askdirectory()
		
		if folder_selected:
			print(folder_selected)
			dir_list = os.listdir(folder_selected)
			movies_filename = [x for x in dir_list if x.endswith('.mkv') or x.endswith('.avi') or x.endswith('.mp4')]
			#print(movies_filename)
			
			for movie_filename in movies_filename:
				movie_filename_without_extension = remove_file_extension(movie_filename)

				if f'{movie_filename_without_extension}.srt' not in dir_list:
					print(movie_filename)
					
					# get season and episode from filename
					se_and_ep_from_filename = get_se_and_ep_from_filename(movie_filename)

					sub_id = None
					if se_and_ep_from_filename:
						# movie id is in middle of href
						res = search_movie_name_with_se_and_ep(sublanguageid, movie_filename_without_extension, se_and_ep_from_filename)
						sub_id = get_sub_id_from_href(res)
						if sub_id == None:
							print("Subtitle id not found by searching for season and episode.")
						else:
							print("sub_id", sub_id)
					
					if sub_id == None:
						res = search_movie_name(sublanguageid, movie_filename_without_extension)
						# get only files that match season and episode
						#print(res)
						res_se_and_ep = [x for x in res if x['se_and_ep'].lower().replace('[','').replace(']','') in movie_filename.lower()]
						#print(res_se_and_ep)
						if len(res_se_and_ep):
							# movie id is at the end of href:
							sub_id = search_subtitles_for_idmovie(sublanguageid, res_se_and_ep[0]['href'].split('idmovie-')[1])
					
					if sub_id != None:
						try:
							download_file(f'https://dl.opensubtitles.org/en/download/sub/{sub_id}', movie_filename, folder_selected)
						except Exception as e:
							print(e)
							pass
					else:
						print('Sub id not found.')

					print('----------------------------------')

	
	button = Button(root, text="Select a folder with movies...", command=ok)
	button.pack()

	mainloop()					


if __name__ == '__main__':
	main()
	#unittest.main()