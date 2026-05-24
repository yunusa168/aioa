import magic

ALLOWED_MIMES = {'image/jpeg', 'image/png', 'image/webp'}

def valider_fichier_bulletin(fichier) -> tuple[bool, str]:
    """
    Valide un fichier uploadé pour l'analyse de bulletin.
    Retourne (valide: bool, message: str).
    """
    if fichier.size > 10 * 1024 * 1024:
        return False, "Fichier trop grand (max 10 Mo)."
    
    fichier.seek(0)
    mime = magic.from_buffer(fichier.read(2048), mime=True)
    fichier.seek(0)
    
    if mime not in ALLOWED_MIMES:
        return False, f"Format invalide. JPG/PNG/WebP uniquement."
    
    # Vérifier que ce n'est pas un fichier déguisé
    if not fichier.name.lower().split('.')[-1] in ['jpg', 'jpeg', 'png', 'webp']:
        return False, "Extension de fichier non reconnue."
    
    return True, "OK"