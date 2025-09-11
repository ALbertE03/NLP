
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
    
    total_articles = sum(len(data['articles']) for data in scraped_data)
    print(f"Total de etiquetas <article> encontradas: {total_articles}")

if __name__ == "__main__":
    main()
