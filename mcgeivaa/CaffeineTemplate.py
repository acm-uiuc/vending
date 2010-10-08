from pml import PML
from McGeivaa import *

def caffeine_template(path):
	pml = PML()
	pml.set("page_title", "Caffeine - Official Provider of Soda for ACM@UIUC Members")
	try:
		drinks = Environment.tool.db.getItems()
	except:
		drinks = []
	pml.set("drinks", drinks)
	return pml.get_output(path)
