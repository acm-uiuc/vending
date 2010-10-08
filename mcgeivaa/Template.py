from pml import PML

def template():
    pml = PML()

    pml.set("title", "Caffeine")

    drinks = ['Soda', 'Diet Soda', 'Water', 'Tea', 'Coffee', 'Bleach', 'More Soda', 'Lol']

    pml.set('drinks', drinks)

    return pml.get_output("testpage.html")
