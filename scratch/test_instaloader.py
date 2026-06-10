import instaloader

L = instaloader.Instaloader()

try:
    print("Carregando perfil 'ifbaiano'...")
    profile = instaloader.Profile.from_username(L.context, "ifbaiano")
    print("Perfil carregado com sucesso!")
    print("Seguidores:", profile.followers)
    print("Postagens:", profile.mediacount)
    
    print("\nBuscando as 3 últimas postagens:")
    count = 0
    for post in profile.get_posts():
        count += 1
        print(f"\n--- POST {count} ---")
        print("Shortcode:", post.shortcode)
        print("Date (UTC):", post.date_utc)
        print("Is Video/Reel:", post.is_video)
        print("Caption:", post.caption[:100] if post.caption else "Sem legenda")
        print("Link:", f"https://www.instagram.com/p/{post.shortcode}/")
        if count >= 3:
            break
except Exception as e:
    print("Erro no Instaloader:", e)
