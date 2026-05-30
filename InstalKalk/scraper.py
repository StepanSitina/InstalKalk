import random

def search_products(query: str):
    """
    Tato funkce modulárně zastupuje vyhledávání z eshopů.
    Pro reálné nasazení sem lze doplnit web scraping přes BeautifulSoup / Playwright 
    nebo napojení na dodavatelská API.
    """
    
    # Simulace zpoždění a vyhledávání
    shops = ["OBI", "Hornbach", "DEK", "Ptáček", "Bauhaus"]
    results = []
    
    # Vygenerujeme 25 fiktivních produktů, ať je co stránkovat
    for i in range(1, 26):
        shop = random.choice(shops)
        price_base = random.randint(50, 2000)
        # Použijeme jednoduchý textový placeholder jako obrázek
        img_id = random.randint(1, 100)
        
        results.append({
            "name": f"{query} - Varianta {i}",
            "shop": shop,
            "price": float(price_base),
            "url": f"https://www.{shop.lower()}.cz/hledani?q={query.replace(' ', '+')}",
            "image_url": f"https://picsum.photos/seed/{img_id}{i}/400/400" # Náhodný dummy obrázek
        })
        
    return results