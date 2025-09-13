
from scraper import Scraper

def main():
    json_file_path = "Data/teleSUR_tv"
      
    scraper = Scraper()
    
    output_dir = "Data_articles"
    
    print("Iniciando scraping de URLs de teleSUR...")
    print("-" * 50)
    
    scraped_data = scraper.scrape_urls_from_data(json_file_path, output_dir)
    
    print("-" * 50)
    print(f"Scraping completado. Se procesaron {len(scraped_data)} artículos.")
    print(f"Los archivos se guardaron en: {output_dir}")
    
    articles_with_text = sum(1 for data in scraped_data if data.get('text', '').strip())
    print(f"Total de artículos con contenido de texto: {articles_with_text}")

if __name__ == "__main__":
    main()
