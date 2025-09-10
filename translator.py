import os
from argostranslate import package, translate

# Sæt stien til modellerne i projektmappen
os.environ["ARGOSTRANSLATE_PACKAGE_DIR"] = os.path.join(os.path.dirname(__file__), "argos_packages")

def oversæt(tekst, fra_sprog='pl', mål_sprog='da'):
    """
    Oversæt tekst fra polsk/tysk til dansk via engelsk.
    Kræver at modellerne (pl→en, de→en, en→da) ligger i argos_packages/.
    Eksempel: oversæt("Der Vogel ist eine Maus", fra_sprog='de', mål_sprog='da')
    """
    try:
        installed_languages = translate.get_installed_languages()
        from_code = next(filter(lambda x: x.code == fra_sprog, installed_languages))
        en_code = next(filter(lambda x: x.code == 'en', installed_languages))
        to_code = next(filter(lambda x: x.code == mål_sprog, installed_languages))

        # Oversæt til engelsk først
        translation_en = from_code.get_translation(en_code)
        engelsk_tekst = translation_en.translate(tekst)

        # Oversæt fra engelsk til dansk
        translation_da = en_code.get_translation(to_code)
        return translation_da.translate(engelsk_tekst)
    except Exception as e:
        print(f"Fejl ved oversættelse: {e}")
        return tekst  # Returner originalteksten, hvis noget går galt
