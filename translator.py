import os
from argostranslate import package, translate
from libretranslatepy import LibreTranslateAPI

def oversæt(tekst, fra_sprog='de', mål_sprog='da'):
    """
    Oversætter tekst til dansk (da) efter følgende regler:
    1. Dansk (da) → Ingen oversættelse.
    2. Engelsk (en) → Direkte en→da (uden at gå via en→en).
    3. Alle andre sprog → Via engelsk (fra→en→da).
    """
    # 1. Dansk: Ingen oversættelse
    if fra_sprog == 'da':
        return tekst

    # 2. Engelsk: Direkte en→da
    if fra_sprog == 'en':
        return _oversæt_direkte(tekst, 'en', 'da')

    # 3. Alle andre sprog: Via engelsk (fra→en→da)
    return _oversæt_via_engelsk(tekst, fra_sprog, 'da')

def _oversæt_direkte(tekst, fra_sprog, mål_sprog):
    """Oversætter direkte fra→mål (bruges til en→da)."""
    try:
        os.environ["ARGOSTRANSLATE_PACKAGE_DIR"] = os.path.join(os.path.dirname(__file__), "argos_packages")
        for model_file in os.listdir("argos_packages"):
            if model_file.endswith(".argosmodel"):
                package.install_from_path(os.path.join("argos_packages", model_file))

        langs = translate.get_installed_languages()
        from_code = next(l for l in langs if l.code == fra_sprog)
        to_code = next(l for l in langs if l.code == mål_sprog)

        translation = from_code.get_translation(to_code)
        result = translation.translate(tekst)
        if result != tekst:  # Valider oversættelsen
            print(f"DEBUG: {fra_sprog}→{mål_sprog}: '{tekst}' → '{result}'")
            return result
    except Exception as e:
        print(f"ArgosTranslate ({fra_sprog}→{mål_sprog}) fejlede: {e}")

    # Backup: LibreTranslate
    try:
        lt = LibreTranslateAPI("https://translate.argosopentech.com/")
        result = lt.translate(tekst, fra_sprog, mål_sprog)
        print(f"DEBUG: Backup (LibreTranslate, {fra_sprog}→{mål_sprog}): '{tekst}' → '{result}'")
        return result
    except Exception as e:
        print(f"LibreTranslate ({fra_sprog}→{mål_sprog}) fejlede: {e}")
        return f"[Oversættelse fejlede: {tekst}]"

def _oversæt_via_engelsk(tekst, fra_sprog, mål_sprog):
    """Oversætter via engelsk (fra→en→mål)."""
    try:
        os.environ["ARGOSTRANSLATE_PACKAGE_DIR"] = os.path.join(os.path.dirname(__file__), "argos_packages")
        for model_file in os.listdir("argos_packages"):
            if model_file.endswith(".argosmodel"):
                package.install_from_path(os.path.join("argos_packages", model_file))

        langs = translate.get_installed_languages()
        from_code = next(l for l in langs if l.code == fra_sprog)
        en_code = next(l for l in langs if l.code == 'en')
        to_code = next(l for l in langs if l.code == mål_sprog)

        # Trin 1: fra_sprog → en
        translation_en = from_code.get_translation(en_code)
        engelsk_tekst = translation_en.translate(tekst)
        if engelsk_tekst == tekst:
            raise ValueError(f"Kunne ikke oversætte '{tekst}' til engelsk")

        # Trin 2: en → mål_sprog
        translation_final = en_code.get_translation(to_code)
        result = translation_final.translate(engelsk_tekst)
        print(f"DEBUG: {fra_sprog}→en→{mål_sprog}: '{tekst}' → '{result}'")
        return result
    except Exception as e:
        print(f"ArgosTranslate ({fra_sprog}→en→{mål_sprog}) fejlede: {e}")

        # Backup: LibreTranslate (direkte fra→mål)
        try:
            lt = LibreTranslateAPI("https://translate.argosopentech.com/")
            result = lt.translate(tekst, fra_sprog, mål_sprog)
            print(f"DEBUG: Backup (LibreTranslate, {fra_sprog}→{mål_sprog}): '{tekst}' → '{result}'")
            return result
        except Exception as e:
            print(f"LibreTranslate ({fra_sprog}→{mål_sprog}) fejlede: {e}")
            return f"[Oversættelse fejlede: {tekst}]"
