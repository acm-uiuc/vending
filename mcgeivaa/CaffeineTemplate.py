from pml import PML
from McGeivaa import *

def caffeine_template():
    pml = PML()

    pml.set("page_title", "Caffeine - Official Provider of Soda for ACM@UIUC Members")
    
    drinks = Environment.tool.db.getItems()
    
    pml.set("drinks", drinks)
    
    print pml.get_output("caffeine.html")

caffeine_template()
