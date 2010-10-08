from pml import PML
from McGeivaa import *

def caffeine_template(path):
	pml = PML()
	pml.set("globals", globals())
	pml.set("locals", locals())
	return pml.get_output(path)
