import os
from argostranslate import package, translate
from libretranslatepy import LibreTranslateAPI

def oversæt(tekst, fra_sprog='de', mål_sprog='da'):
    """
    Oversætter tekst fra `fra_sprog` til `mål_sprog` via engelsk.
    Bruger ArgosTranslate (offline) som primær løsning,
    og LibreTranslate (online) som backup hvis Argos fehler.
    """
    try:
        # --- ArgosTranslate (offline) ---
        os.environ["ARGOSTRANSLATE_PACKAGE_DIR"] = os.path.join(os.path.dirname(__file__), "argos_packages")
        for model_file in os.listdir("argos_packages"):
            if model_file.endswith(".argosmodel"):
                package.install_from_path(os.path.join("argos_packages", model_file))

        langs = translate.get_installed_languages()
        from_code = next(l for l in langs if l.code == fra_sprog)
        en_code = next(l for l in langs if l.code == 'en')
        to_code = next(l for l in langs if l.code == mål_sprog)

        # Oversæt via engelsk
        translation_en = from_code.get_translation(en_code)
        engelsk_tekst = translation_en.translate(tekst)

        # Valider at teksten er blevet oversat
        if engelsk_tekst == tekst:
            raise ValueError("ArgosTranslate oversatte ikke teksten")

        translation_final = en_code.get_translation(to_code)
        result = translation_final.translate(engelsk_tekst)
        print(f"DEBUG: {fra_sprog}→en→{mål_sprog}: '{tekst}' → '{result}'")
        return result

    except Exception as e:
        print(f"ArgosTranslate fejlede: {e}")
        # --- Backup: LibreTranslate (online) ---
        try:
            lt = LibreTranslateAPI("https://translate.argosopentech.com/")
            result = lt.translate(tekst, fra_sprog, mål_sprog)
            print(f"DEBUG: Backup (LibreTranslate): '{tekst}' → '{result}'")
            return result
        except Exception as e:
            print(f"LibreTranslate fejlede: {e}")
            return f"[Oversættelse fejlede: {tekst}]"
