from bs4 import BeautifulSoup
import os 
import requests
import re
import json
import time
from urllib.parse import urlparse

class Scraper:
    def __init__(self, data_path="Data/teleSUR_tv"):
        self.data_path = data_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_urls_from_json(self, json_file_path):
        """
        Extrae todas las URLs del archivo JSON de mensajes de Telegram
        manteniendo la referencia al archivo y posición original
        """
        urls_with_metadata = []
        try:
            for i in os.listdir(json_file_path):
                year_path = os.path.join(json_file_path, i)
                if os.path.isdir(year_path):
                    for j in os.listdir(year_path):
                        json_file = os.path.join(year_path, j)
                        if j.endswith('.json'):
                            with open(json_file, 'r', encoding='utf-8') as file:
                                messages = json.load(file)
                            
                            for index, message in enumerate(messages):
                                text = message.get('text', '')
                                url_pattern = r'https?://[^\s\n]+'
                                found_urls = re.findall(url_pattern, text)
                                
                                for url in found_urls:
                                    url_metadata = {
                                        'url': url,
                                        'json_file': json_file,
                                        'message_index': index,
                                        'message_id': message.get('message_id'),
                                        'date': message.get('date'),
                                        'text': text,
                                        'photo_path': message.get('photo_path'),
                                        'views': message.get('views'),
                                        'reactions': message.get('reactions', {}),
                                        'total_reactions': message.get('total_reactions', 0)
                                    }
                                    urls_with_metadata.append(url_metadata)
                
        except Exception as e:
            print(f"Error al leer el archivo JSON: {e}")
            
        return urls_with_metadata  
    
    def scrape_article_content(self, url, url_metadata=None):
        """
        Hace scraping de una URL y extrae el contenido de las etiquetas <article>
        """
        try:
            print(f"Haciendo scraping de: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article')
            
            content = {
                'url': url,
                'title': '',
                'articles': [],
                'source_metadata': url_metadata 
            }
            
            title_tag = soup.find('title')
            if title_tag:
                content['title'] = title_tag.get_text().strip()

            for i, article in enumerate(articles):
                article_content = {
                    'article_number': i + 1,
                    'text': article.get_text().strip(),
                    'html': str(article)
                }
                content['articles'].append(article_content)
            
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"Error al hacer request a {url}: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al procesar {url}: {e}")
            return None
    
    def scrape_urls_from_data(self, json_file_path, output_dir="scraped_articles"):
        """
        Extrae URLs del JSON y hace scraping de cada una manteniendo referencias
        """
        os.makedirs(output_dir, exist_ok=True)
        
        urls_with_metadata = self.extract_urls_from_json(json_file_path)
        print(f"Encontradas {len(urls_with_metadata)} URLs con metadata")
        
        seen_urls = set()
        telesur_urls_metadata = []
        for url_data in urls_with_metadata:
            if 'telesurtv.net' in url_data['url'] and url_data['url'] not in seen_urls:
                telesur_urls_metadata.append(url_data)
                seen_urls.add(url_data['url'])
        
        print(f"URLs únicas de teleSUR: {len(telesur_urls_metadata)}")
        
        scraped_data = []
        
        for i, url_data in enumerate(telesur_urls_metadata, 1):
            url = url_data['url']
            print(f"Procesando {i}/{len(telesur_urls_metadata)}: {url}")
            print(f"  Origen: {url_data['json_file']} (mensaje #{url_data['message_index']})")
            
            article_data = self.scrape_article_content(url, url_data)
            
            if article_data and article_data['articles']:
                scraped_data.append(article_data)
                
                safe_filename = re.sub(r'[^\w\-_.]', '_', urlparse(url).path.split('/')[-1])
                if not safe_filename:
                    safe_filename = f"article_{i}"
                    
                output_file = os.path.join(output_dir, f"{safe_filename}.json")
                
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=2)
                    print(f"Guardado: {output_file}")
                except Exception as e:
                    print(f"Error al guardar {output_file}: {e}")
            else:
                print(f"No se encontraron artículos en: {url}")
            
            time.sleep(1)

        consolidated_file = os.path.join(output_dir, "all_articles_with_metadata.json")
        try:
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=2)
            print(f"Archivo consolidado guardado: {consolidated_file}")
        except Exception as e:
            print(f"Error al guardar archivo consolidado: {e}")
        
        index_data = []
        for i, article_data in enumerate(scraped_data):
            metadata = article_data.get('source_metadata', {})
            for j, article in enumerate(article_data.get('articles', [])):
                index_entry = {
                    'article_id': f"{i}_{j}",
                    'url': article_data['url'],
                    'title': article_data['title'],
                    'article_number': article['article_number'],
                    'original_json_file': metadata.get('json_file'),
                    'message_index': metadata.get('message_index'),
                    'message_id': metadata.get('message_id'),
                    'date': metadata.get('date'),
                    'original_text': metadata.get('text'),
                    'photo_path': metadata.get('photo_path'),
                    'views': metadata.get('views'),
                    'reactions': metadata.get('reactions'),
                    'total_reactions': metadata.get('total_reactions')
                }
                index_data.append(index_entry)
        
        index_file = os.path.join(output_dir, "articles_index.json")
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            print(f"Índice de artículos guardado: {index_file}")
        except Exception as e:
            print(f"Error al guardar índice: {e}")
        
        return scraped_data
    
    def find_article_by_message(self, index_file_path, message_id=None, json_file=None, message_index=None):
        """
        Busca artículos basándose en la referencia del mensaje original
        """
        try:
            with open(index_file_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            results = []
            for entry in index_data:
                match = False
                
                if message_id and entry.get('message_id') == message_id:
                    match = True
                elif json_file and message_index is not None:
                    if (entry.get('original_json_file', '').endswith(json_file) and 
                        entry.get('message_index') == message_index):
                        match = True
                
                if match:
                    results.append(entry)
            
            return results
            
        except Exception as e:
            print(f"Error al buscar en el índice: {e}")
            return []
    
    def get_original_message(self, json_file_path, message_index):
        """
        Obtiene el mensaje original completo del archivo JSON
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            if 0 <= message_index < len(messages):
                return messages[message_index]
            else:
                print(f"Índice {message_index} fuera de rango en {json_file_path}")
                return None
                
        except Exception as e:
            print(f"Error al obtener mensaje original: {e}")
            return None
    
    def export_to_csv(self, index_file_path, output_csv="articles_export.csv"):
        """
        Exporta el índice de artículos a un archivo CSV para análisis
        """
        try:
            import csv
            
            with open(index_file_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'article_id', 'url', 'title', 'article_number',
                    'message_id', 'date', 'views', 'total_reactions',
                    'original_json_file', 'message_index', 'photo_path'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in index_data:
                    row = {field: entry.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            print(f"Datos exportados a: {output_csv}")
            return True
            
        except Exception as e:
            print(f"Error al exportar a CSV: {e}")
            return False
    
    def get_article_statistics(self, index_file_path):
        """
        Genera estadísticas sobre los artículos extraídos
        """
        try:
            with open(index_file_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            stats = {
                'total_articles': len(index_data),
                'unique_urls': len(set(entry['url'] for entry in index_data)),
                'date_range': {
                    'earliest': min(entry['date'] for entry in index_data if entry['date']),
                    'latest': max(entry['date'] for entry in index_data if entry['date'])
                },
                'total_views': sum(entry.get('views', 0) for entry in index_data),
                'total_reactions': sum(entry.get('total_reactions', 0) for entry in index_data),
                'articles_by_json': {},
                'articles_with_photos': sum(1 for entry in index_data if entry.get('photo_path'))
            }
            
            for entry in index_data:
                json_file = os.path.basename(entry.get('original_json_file', 'Unknown'))
                if json_file not in stats['articles_by_json']:
                    stats['articles_by_json'][json_file] = 0
                stats['articles_by_json'][json_file] += 1
            
            return stats
            
        except Exception as e:
            print(f"Error al generar estadísticas: {e}")
            return None
