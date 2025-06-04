import sys
import os
import json
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 20250527
import openai
# from openai import OpenAI

# Configuração do caminho para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__, 
            static_folder='../src/static',
            template_folder='../src/templates')

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB

# Configuração da API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Verifica se a pasta de uploads existe, se não, cria
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    print("Acessando rota principal '/'")
    #return render_template('index.html')
    return send_from_directory('../src/static', 'metadata.html')

@app.route('/mint')
def mint_page():
    print("Acessando página de mint '/mint'")
    return send_from_directory('../src/static', 'mint.html')

@app.route('/metadata')
def metadata_page():
    print("Acessando página de criação de metadados '/metadata'")
    return send_from_directory('../src/static', 'metadata.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    print("Recebendo requisição de upload")
    # Verifica se há arquivo na requisição
    if 'file' not in request.files:
        print("Erro: Nenhum arquivo enviado")
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    # Verifica se o nome do arquivo está vazio
    if file.filename == '':
        print("Erro: Nenhum arquivo selecionado")
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    # Verifica se o arquivo é permitido
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Salvando arquivo em: {filepath}")
        file.save(filepath)
        
        # Verifica se as chaves da API do Pinata estão configuradas
        pinata_api_key = os.getenv('PINATA_API_KEY')
        pinata_secret_key = os.getenv('PINATA_SECRET_KEY')
        
        if not pinata_api_key or not pinata_secret_key:
            print("Erro: Chaves da API do Pinata não configuradas")
            # Não remove o arquivo para depuração
            return jsonify({
                'error': 'Chaves da API do Pinata não configuradas. Verifique seu arquivo .env',
                'debug_info': {
                    'file_saved': filepath,
                    'pinata_api_key_set': pinata_api_key is not None,
                    'pinata_secret_key_set': pinata_secret_key is not None
                }
            }), 500
        
        # Envia o arquivo para o Pinata
        try:
            print("Tentando enviar para o Pinata")
            pinata_response = pin_to_pinata(filepath, filename)
            
            # Remove o arquivo após o upload para o Pinata
            os.remove(filepath)
            print("Arquivo enviado com sucesso e removido localmente")
            
            return jsonify(pinata_response), 200
        except Exception as e:
            print(f"Erro ao enviar para o Pinata: {str(e)}")
            # Não remove o arquivo em caso de erro para depuração
            return jsonify({
                'error': str(e),
                'debug_info': {
                    'file_saved': filepath
                }
            }), 500
    
    print(f"Erro: Tipo de arquivo não permitido: {file.filename}")
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

def pin_to_pinata(filepath, filename):
    """
    Envia um arquivo para o Pinata e retorna o hash IPFS
    """
    # Obter as chaves da API do Pinata das variáveis de ambiente
    pinata_api_key = os.getenv('PINATA_API_KEY')
    pinata_secret_key = os.getenv('PINATA_SECRET_KEY')
    
    print(f"Chaves Pinata configuradas: API Key: {'Sim' if pinata_api_key else 'Não'}, Secret Key: {'Sim' if pinata_secret_key else 'Não'}")
    
    if not pinata_api_key or not pinata_secret_key:
        raise Exception("Chaves da API do Pinata não configuradas")
    
    # URL da API do Pinata para upload de arquivos
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    # Cabeçalhos com as chaves de autenticação
    headers = {
        'pinata_api_key': pinata_api_key,
        'pinata_secret_api_key': pinata_secret_key
    }
    
    # Preparar o arquivo para upload
    with open(filepath, 'rb') as file:
        files = {
            'file': (filename, file)
        }
        
        # Metadados do arquivo
        payload = {
            'pinataMetadata': json.dumps({
                'name': f'NFT-{filename}'
            }),
            'pinataOptions': json.dumps({
                'cidVersion': 1
            })
        }
        
        print(f"Enviando arquivo para o Pinata: {filename}")
        # Enviar o arquivo para o Pinata
        response = requests.post(url, files=files, data=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro na resposta do Pinata: Status {response.status_code}, Resposta: {response.text}")
        raise Exception(f"Erro ao enviar para o Pinata: {response.text}")
    
    print(f"Resposta do Pinata: {response.text}")
    # Retorna os dados da resposta do Pinata
    return response.json()

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analisa uma imagem IPFS usando a API do OpenAI para extrair sentimentos, 
    psicologia das cores, símbolos e códigos de linguagem
    """
    print("Recebendo requisição para análise de imagem")
    data = request.json
    
    if not data or 'image_hash' not in data:
        print("Erro: Hash da imagem não fornecido")
        return jsonify({'error': 'Hash da imagem não fornecido'}), 400
    
    image_hash = data['image_hash']
    #image_url = f"https://ipfs.io/ipfs/{image_hash}"
    # linha abaixo com xxx deve ser modificada apenas quando usa a API da OPENAI, 
    # porque se usar https://ipfs.io/ipfs/ da erro no download da OPENAI
    # para gerar ometadado no Json do Pinata manter o https://ipfs.io/ipfs/
    
    image_url = f"https://gateway.pinata.cloud/ipfs/{image_hash}"
    	
    print(f"Analisando imagem: {image_url}")
    
    # Verifica se a chave da API OpenAI está configurada
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("Erro: Chave da API OpenAI não configurada")
        return jsonify({
            'error': 'Chave da API OpenAI não configurada. Verifique seu arquivo .env',
        }), 500
    
    try:
        # Chamada para a API do OpenAI para análise da imagem
        analysis = analyze_image_with_openai(image_url)
        print("Análise concluída com sucesso")
        return jsonify(analysis), 200
    except Exception as e:
        print(f"Erro ao analisar imagem: {str(e)}")
        return jsonify({'error': str(e)}), 500

def analyze_image_with_openai(image_url):
    """
    Utiliza a API do OpenAI para analisar uma imagem e extrair informações sobre
    sentimentos, psicologia das cores, símbolos e códigos de linguagem
    
    Compatível com diferentes versões da biblioteca OpenAI
    """
    try:
        print(f"Enviando requisição para OpenAI com a URL da imagem: {image_url}")
        
        # Prompt para a análise da imagem
        prompt = f"""
        Analise esta imagem NFT disponível em {image_url} e forneça uma análise detalhada sobre:

        1. Análise de sentimentos: Quais emoções e sentimentos esta imagem evoca?
        2. Psicologia das cores: Analise as cores predominantes e seus significados psicológicos.
        3. Relação entre símbolos: Por símbolos, entende-se ícones, formas, imagens ou objetos presentes na arte que carregam significados culturais, históricos, artísticos ou subjetivos.? Explique.	
        4. Códigos de linguagem visual: Quais elementos visuais se destacam e o que eles comunicam?

        Formate sua resposta em JSON com as seguintes chaves:
        - sentiment_analysis: texto detalhado sobre os sentimentos evocados
        - color_psychology: análise das cores e seus significados
        - symbol_relation: possíveis conexões, significados ou interpretações de símbolos presentes na imagem
        - visual_language: análise dos elementos visuais e sua comunicação
        - keywords: lista de 5-10 palavras-chave que descrevem a imagem
        - attributes: lista de atributos no formato [{{"trait_type": "Emoção Primária", "value": "valor"}}, ...]
        """
        
        # Método compatível com diferentes versões da API OpenAI
        try:
            # Tentativa com a versão mais recente da API
		        # model="gpt-4-vision-preview",
		        # model="gpt-4.5-preview",
		        # model="gpt-4o",                   
            print("Tentando usar a versão mais recente da API OpenAI")
            
            # 20250527
            response = openai.ChatCompletion.create(
                model="gpt-4.5-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=1000
            )   
            
            '''
            # 20250527
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
				    response = client.chat.completions.create(
				    model="gpt-4.5-preview",
				    messages=[
				        {"role": "user", "content": [
				            {"type": "text", "text": prompt},
				            {"type": "image_url", "image_url": {"url": image_url}}
				        ]}
				    ],
				    max_tokens=1000
						)
            '''
            # Extrair a resposta
            if hasattr(response, 'choices') and len(response.choices) > 0:
                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    result = response.choices[0].message.content
                else:
                    result = response.choices[0].get('message', {}).get('content', '')
            else:
                result = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
        except (AttributeError, TypeError) as e:
            print(f"Erro com a versão mais recente da API: {str(e)}. Tentando método alternativo.")
            
            # Tentativa com versão alternativa da API
            response = openai.chat.completions.create(
                model="gpt-4-vision",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Extrair a resposta
            if hasattr(response, 'choices') and len(response.choices) > 0:
                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    result = response.choices[0].message.content
                else:
                    result = response.choices[0].get('message', {}).get('content', '')
            else:
                result = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        print(f"Resposta da OpenAI recebida: {result[:100]}...")
        
        # Tentar parsear o JSON da resposta
        try:
            # Encontrar o início e fim do JSON na resposta
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                # Se não encontrar JSON válido, criar estrutura manualmente
                print("JSON não encontrado na resposta, criando estrutura manualmente")
                analysis = {
                    "sentiment_analysis": extract_section(result, "Análise de sentimentos"),
                    "color_psychology": extract_section(result, "Psicologia das cores"),
                    "symbol_relation": extract_section(result, "Relação entre símbolos"),
                    "visual_language": extract_section(result, "Códigos de linguagem visual"),
                    "keywords": extract_keywords(result),
                    "attributes": generate_attributes(result)
                }
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta, criando estrutura manualmente")
            analysis = {
                "sentiment_analysis": extract_section(result, "Análise de sentimentos"),
                "color_psychology": extract_section(result, "Psicologia das cores"),
                "symbol_relation": extract_section(result, "Relação entre símbolos"),
                "visual_language": extract_section(result, "Códigos de linguagem visual"),
                "keywords": extract_keywords(result),
                "attributes": generate_attributes(result)
            }
        
        return analysis
    
    except Exception as e:
        print(f"Erro na chamada para OpenAI: {str(e)}")
        raise Exception(f"Erro ao analisar imagem com OpenAI: {str(e)}")

def extract_section(text, section_title):
    """
    Extrai uma seção específica do texto da resposta
    """
    try:
        # Procura pelo título da seção
        start_idx = text.find(section_title)
        if start_idx == -1:
            return "Informação não disponível"
        
        # Encontra o início do conteúdo após o título
        start_idx = text.find(":", start_idx) + 1
        if start_idx == 0:
            return "Informação não disponível"
        
        # Procura pelo próximo título de seção ou fim do texto
        next_section_titles = ["Análise de sentimentos", "Psicologia das cores", "Relação entre símbolos ", "Códigos de linguagem visual", "Palavras-chave", "Atributos"]
        end_idx = len(text)
        
        for title in next_section_titles:
            if title != section_title:
                temp_idx = text.find(title, start_idx)
                if temp_idx != -1 and temp_idx < end_idx:
                    end_idx = temp_idx
        
        # Extrai e limpa o conteúdo
        content = text[start_idx:end_idx].strip()
        return content
    except Exception as e:
        print(f"Erro ao extrair seção {section_title}: {str(e)}")
        return "Informação não disponível"

def extract_keywords(text):
    """
    Extrai palavras-chave do texto da resposta
    """
    try:
        # Procura por palavras-chave na resposta
        keywords_section = text.lower().find("palavras-chave")
        if keywords_section == -1:
            # Tenta encontrar a seção de keywords
            keywords_section = text.lower().find("keywords")
        
        if keywords_section == -1:
            # Gera palavras-chave genéricas se não encontrar
            return ["arte", "nft", "digital", "criativo", "único"]
        
        # Encontra o início do conteúdo após o título
        start_idx = text.find(":", keywords_section) + 1
        if start_idx == 0:
            return ["arte", "nft", "digital", "criativo", "único"]
        
        # Procura pelo próximo título de seção ou fim do texto
        end_idx = len(text)
        next_sections = ["atributos", "attributes"]
        
        for section in next_sections:
            temp_idx = text.lower().find(section, start_idx)
            if temp_idx != -1 and temp_idx < end_idx:
                end_idx = temp_idx
        
        # Extrai e processa as palavras-chave
        keywords_text = text[start_idx:end_idx].strip()
        
        # Tenta diferentes formatos de palavras-chave
        if "[" in keywords_text and "]" in keywords_text:
            # Formato de lista JSON
            start_list = keywords_text.find("[")
            end_list = keywords_text.find("]") + 1
            try:
                keywords_list = json.loads(keywords_text[start_list:end_list])
                return keywords_list
            except:
                pass
        
        # Formato de lista separada por vírgulas
        keywords = [k.strip().strip('"\'') for k in keywords_text.split(",")]
        
        # Limita a 10 palavras-chave
        return keywords[:10]
    except Exception as e:
        print(f"Erro ao extrair palavras-chave: {str(e)}")
        return ["arte", "nft", "digital", "criativo", "único"]

def generate_attributes(text):
    """
    Gera atributos a partir do texto da resposta
    """
    try:
        # Procura por atributos na resposta
        attributes_section = text.lower().find("atributos")
        if attributes_section == -1:
            # Tenta encontrar a seção de attributes
            attributes_section = text.lower().find("attributes")
        
        if attributes_section == -1:
            # Gera atributos genéricos se não encontrar
            return [
                {"trait_type": "Tipo", "value": "Arte Digital"},
                {"trait_type": "Estilo", "value": "Único"},
                {"trait_type": "Raridade", "value": "Comum"}
            ]
        
        # Encontra o início do conteúdo após o título
        start_idx = text.find(":", attributes_section) + 1
        if start_idx == 0:
            return [
                {"trait_type": "Tipo", "value": "Arte Digital"},
                {"trait_type": "Estilo", "value": "Único"},
                {"trait_type": "Raridade", "value": "Comum"}
            ]
        
        # Extrai o texto dos atributos
        attributes_text = text[start_idx:].strip()
        
        # Tenta parsear como JSON se estiver no formato de lista
        if "[" in attributes_text and "]" in attributes_text:
            start_list = attributes_text.find("[")
            end_list = attributes_text.rfind("]") + 1
            try:
                attributes_list = json.loads(attributes_text[start_list:end_list])
                return attributes_list
            except:
                pass
        
        # Se não conseguir parsear, extrai manualmente
        # Procura por padrões como "Emoção Primária: Alegria"
        attributes = []
        lines = attributes_text.split("\n")
        
        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                trait_type = parts[0].strip().strip('"\'')
                value = parts[1].strip().strip('"\'')
                
                if trait_type and value:
                    attributes.append({"trait_type": trait_type, "value": value})
        
        # Se não encontrou atributos válidos, gera alguns baseados nas seções
        if not attributes:
            # Extrai informações das outras seções para criar atributos
            sentiment = extract_section(text, "Análise de sentimentos")
            colors = extract_section(text, "Psicologia das cores")
            symbol = extract_section(text, "Relação entre símbolos ")
            
            # Cria atributos básicos
            attributes = [
                {"trait_type": "Sentimento Predominante", "value": extract_main_sentiment(sentiment)},
                {"trait_type": "Cor Principal", "value": extract_main_color(colors)},
                {"trait_type": "Símbolos Relacionado", "value": extract_symbol(symbol)}
            ]
        
        return attributes
    except Exception as e:
        print(f"Erro ao gerar atributos: {str(e)}")
        return [
            {"trait_type": "Tipo", "value": "Arte Digital"},
            {"trait_type": "Estilo", "value": "Único"},
            {"trait_type": "Raridade", "value": "Comum"}
        ]

def extract_main_sentiment(sentiment_text):
    """
    Extrai o sentimento principal do texto de análise de sentimentos
    """
    # Lista de sentimentos comuns para procurar
    common_sentiments = [
        "alegria", "felicidade", "tristeza", "raiva", "medo", "surpresa", 
        "nojo", "antecipação", "confiança", "calma", "serenidade", "amor",
        "paz", "tranquilidade", "ansiedade", "melancolia", "nostalgia",
        "esperança", "admiração", "curiosidade"
    ]
    
    sentiment_text = sentiment_text.lower()
    
    # Procura por sentimentos comuns no texto
    for sentiment in common_sentiments:
        if sentiment in sentiment_text:
            # Capitaliza a primeira letra
            return sentiment.capitalize()
    
    # Retorno padrão se nenhum sentimento for encontrado
    return "Neutro"

def extract_main_color(color_text):
    """
    Extrai a cor principal do texto de psicologia das cores
    """
    # Lista de cores comuns para procurar
    common_colors = [
        "vermelho", "azul", "verde", "amarelo", "laranja", "roxo", 
        "violeta", "rosa", "marrom", "preto", "branco", "cinza",
        "dourado", "prateado", "turquesa", "índigo", "magenta"
    ]
    
    color_text = color_text.lower()
    
    # Procura por cores comuns no texto
    for color in common_colors:
        if color in color_text:
            # Capitaliza a primeira letra
            return color.capitalize()
    
    # Retorno padrão se nenhuma cor for encontrada
    return "Multicolorido"

def extract_symbol(symbol_text):
    """
    Extrai símbolos relevantes do texto de relação entre símbolos.
    """
   
    # Lista de símbolos para analisar (exemplo, adicione mais conforme seu contexto)
    
    '''
    symbols = [
        "coração", "estrela", "cruz", "pomba", "olho", "fogo", "água", 
        "triângulo", "círculo", "quadrado", "lua", "sol", "serpente", 
        "mão", "relógio", "chave", "borboleta", "máscara"
    ]
    '''
    
    symbols = [
	    # Naturais e Universais
	    "coração",
	    "estrela",
	    "olho",
	    "lua",
	    "sol",
	    "flor",
	    "folha",
	    "árvore",
	    "fogo",
	    "água",
	    "montanha",
	    "cavalo",
	    "gato",
	    "cachorro",
	    "peixe",
	    "pássaro",
	    "borboleta",
	    "pena",
	    "cobra",
	    "urso",
	    "leão",
	    "tigre",
	    
	    # Formas e Ícones Gerais
	    "triângulo",
	    "círculo",
	    "quadrado",
	    "pirâmide",
	    "cruz",
	    "ampulheta",
	    "roda",
	    "anel",
	    "estrela de davi",
	    "yin yang",
	    "infinito",

	    # Urbanos e Tecnológicos
	    "carro",
	    "avião",
	    "predio",
	    "ponte",
	    "óculos",
	    "relógio",
	    "telefone",
	    "computador",
	    "chip",
	    "satélite",
	    "antena",
	    "robô",
	    "engrenagem",
	    "wifi",
	    "dado",

	    # Místicos e Mitológicos
	    "máscara",
	    "olho de hórus",
	    "dragão",
	    "fênix",
	    "tridente",
	    "unicórnio",
	    "anjo",
	    "demônio",
	    "gárgula",
	    "grifo",
	    "cálice",

	    # Religiosos e Espirituais
	    "mão de fátima",
	    "paz",
	    "espada",
	    "coroa",
	    "escudo",
	    "chave",
	    "vela",
	    "cristal",
	    "arco-íris",
	    "relâmpago",
	    "escada",
	    "pomba", # Paz/Espiritualidade
	    "estrela cadente",
	    "martelo" # também mitológico (Thor)
		]

        
    
    symbol_text = symbol_text.lower()
    found_symbols = []
    
    for symbol in symbols:
        if symbol in symbol_text:
            found_symbols.append(symbol.capitalize())
    
    if found_symbols:
        return found_symbols
    else:
        return ["Não identificado"]  # Para manter a compatibilidade
    
    # Retorno padrão se nenhum símbolo for encontrado
    return "Não identificado"

@app.route('/api/create-metadata', methods=['POST'])
def create_metadata():
    """
    Cria e pina os metadados do NFT no Pinata, incluindo análise da imagem
    """
    print("Recebendo requisição para criar metadados")
    data = request.json
    
    if not data or 'name' not in data or 'description' not in data or 'image' not in data:
        print("Erro: Dados incompletos para metadados")
        return jsonify({'error': 'Dados incompletos'}), 400
    
    # Verifica se há análise de imagem
    image_analysis = data.get('image_analysis', None)
    
    # Cria o objeto de metadados conforme padrão ERC-721
    # Usando o formato https://ipfs.io/ipfs/ em vez de ipfs://
    # Usando o formato https://gateway.pinata.cloud/ipfs/ em vez de ipfs://
    
    ''' 
    metadata = {
        'name': data['name'],
        'description': data['description'],
        'image': f"https://ipfs.io/ipfs/{data['image']}",  # Formato HTTP Gateway URL
        'attributes': data.get('attributes', [])
    }
    
    '''

    
    metadata = {
        'name': data['name'],
        'description': data['description'],
        'image': f"https://gateway.pinata.cloud/ipfs/{data['image']}",  # Formato HTTP Gateway URL
        'attributes': data.get('attributes', [])
    }
    
   
    
    # Se houver análise de imagem, enriquece os metadados
    if image_analysis:
        # Adiciona a análise de sentimentos à descrição
        enriched_description = data['description']
        
        if 'sentiment_analysis' in image_analysis:
            enriched_description += f"\n\n**Análise de Sentimentos:**\n{image_analysis['sentiment_analysis']}"
        
        if 'color_psychology' in image_analysis:
            enriched_description += f"\n\n**Psicologia das Cores:**\n{image_analysis['color_psychology']}"
        
        if 'symbol_relation' in image_analysis:
            enriched_description += f"\n\n**Relação entre símbolos :**\n{image_analysis['symbol_relation']}"
        
        if 'visual_language' in image_analysis:
            enriched_description += f"\n\n**Linguagem Visual:**\n{image_analysis['visual_language']}"
        
        # Atualiza a descrição
        metadata['description'] = enriched_description
        
        # Adiciona atributos da análise
        if 'attributes' in image_analysis and image_analysis['attributes']:
            metadata['attributes'].extend(image_analysis['attributes'])
        
        # Adiciona palavras-chave como atributos
        if 'keywords' in image_analysis and image_analysis['keywords']:
            for i, keyword in enumerate(image_analysis['keywords']):
                metadata['attributes'].append({
                    "trait_type": f"Palavra-chave {i+1}",
                    "value": keyword
                })
    
    # Obter as chaves da API do Pinata das variáveis de ambiente
    pinata_api_key = os.getenv('PINATA_API_KEY')
    pinata_secret_key = os.getenv('PINATA_SECRET_KEY')
    
    if not pinata_api_key or not pinata_secret_key:
        print("Erro: Chaves da API do Pinata não configuradas para metadados")
        return jsonify({
            'error': 'Chaves da API do Pinata não configuradas',
            'debug_info': {
                'pinata_api_key_set': pinata_api_key is not None,
                'pinata_secret_key_set': pinata_secret_key is not None
            }
        }), 500
    
    # URL da API do Pinata para pinagem de JSON
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    
    # Cabeçalhos com as chaves de autenticação
    headers = {
        'Content-Type': 'application/json',
        'pinata_api_key': pinata_api_key,
        'pinata_secret_api_key': pinata_secret_key
    }
    
    # Dados para envio com nome de arquivo incluindo extensão .json
    payload = {
        'pinataContent': metadata,
        'pinataMetadata': {
            'name': f"metadata-{data['name']}.json"  # Adicionando extensão .json
        }
    }
    
    try:
        print(f"Enviando metadados para o Pinata: {json.dumps(metadata)}")
        # Enviar os metadados para o Pinata
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"Erro na resposta do Pinata para metadados: Status {response.status_code}, Resposta: {response.text}")
            return jsonify({'error': f"Erro ao enviar metadados para o Pinata: {response.text}"}), 500
        
        print(f"Resposta do Pinata para metadados: {response.text}")
        # Retorna os dados da resposta do Pinata
        return jsonify(response.json()), 200
    except Exception as e:
        print(f"Erro ao enviar metadados: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Nova rota para criar metadados de forma independente (sem mint)
@app.route('/api/create-metadata-only', methods=['POST'])
def create_metadata_only():
    """
    Cria e pina apenas os metadados do NFT no Pinata, sem necessidade de contrato NFT
    """
    print("Recebendo requisição para criar apenas metadados (sem mint)")
    data = request.json
    
    if not data or 'name' not in data or 'description' not in data or 'image' not in data:
        print("Erro: Dados incompletos para metadados")
        return jsonify({'error': 'Dados incompletos'}), 400
    
    # Verifica se há análise de imagem
    image_analysis = data.get('image_analysis', None)
    
    # Cria o objeto de metadados conforme padrão ERC-721
    # Usando o formato https://ipfs.io/ipfs/ em vez de ipfs://
    # Usando o formato https://gateway.pinata.cloud/ipfs/ em vez de ipfs://
    
    '''
        metadata = {
        'name': data['name'],
        'description': data['description'],
        'image': f"https://ipfs.io/ipfs/{data['image']}",  # Formato HTTP Gateway URL
        'attributes': data.get('attributes', [])
    }
    '''
    
    
    metadata = {
        'name': data['name'],
        'description': data['description'],
        'image': f"https://gateway.pinata.cloud/ipfs/{data['image']}",  # Formato HTTP Gateway URL
        'attributes': data.get('attributes', [])
    }
    
    
    
    
    # Se houver análise de imagem, enriquece os metadados
    if image_analysis:
        # Adiciona a análise de sentimentos à descrição
        enriched_description = data['description']
        
        if 'sentiment_analysis' in image_analysis:
            enriched_description += f"\n\n**Análise de Sentimentos:**\n{image_analysis['sentiment_analysis']}"
        
        if 'color_psychology' in image_analysis:
            enriched_description += f"\n\n**Psicologia das Cores:**\n{image_analysis['color_psychology']}"
        
        if 'symbol_relation' in image_analysis:
            enriched_description += f"\n\n**Relação entre símbolos :**\n{image_analysis['symbol_relation']}"
        
        if 'visual_language' in image_analysis:
            enriched_description += f"\n\n**Linguagem Visual:**\n{image_analysis['visual_language']}"
        
        # Atualiza a descrição
        metadata['description'] = enriched_description
        
        # Adiciona atributos da análise
        if 'attributes' in image_analysis and image_analysis['attributes']:
            metadata['attributes'].extend(image_analysis['attributes'])
        
        # Adiciona palavras-chave como atributos
        if 'keywords' in image_analysis and image_analysis['keywords']:
            for i, keyword in enumerate(image_analysis['keywords']):
                metadata['attributes'].append({
                    "trait_type": f"Palavra-chave {i+1}",
                    "value": keyword
                })
    
    # Obter as chaves da API do Pinata das variáveis de ambiente
    pinata_api_key = os.getenv('PINATA_API_KEY')
    pinata_secret_key = os.getenv('PINATA_SECRET_KEY')
    
    if not pinata_api_key or not pinata_secret_key:
        print("Erro: Chaves da API do Pinata não configuradas para metadados")
        return jsonify({
            'error': 'Chaves da API do Pinata não configuradas',
            'debug_info': {
                'pinata_api_key_set': pinata_api_key is not None,
                'pinata_secret_key_set': pinata_secret_key is not None
            }
        }), 500
    
    # URL da API do Pinata para pinagem de JSON
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    
    # Cabeçalhos com as chaves de autenticação
    headers = {
        'Content-Type': 'application/json',
        'pinata_api_key': pinata_api_key,
        'pinata_secret_api_key': pinata_secret_key
    }
    
    # Dados para envio com nome de arquivo incluindo extensão .json
    payload = {
        'pinataContent': metadata,
        'pinataMetadata': {
            'name': f"metadata-{data['name']}.json"  # Adicionando extensão .json
        }
    }
    
    try:
        print(f"Enviando metadados para o Pinata: {json.dumps(metadata)}")
        # Enviar os metadados para o Pinata
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"Erro na resposta do Pinata para metadados: Status {response.status_code}, Resposta: {response.text}")
            return jsonify({'error': f"Erro ao enviar metadados para o Pinata: {response.text}"}), 500
        
        print(f"Resposta do Pinata para metadados: {response.text}")
        
        # Adiciona o metadata completo à resposta para exibição
        response_data = response.json()
        response_data['metadata'] = metadata
        
        # Retorna os dados da resposta do Pinata junto com os metadados
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Erro ao enviar metadados: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Iniciando servidor Flask. Pasta de uploads: {UPLOAD_FOLDER}")
    print(f"Verificando existência da pasta de uploads: {'Existe' if os.path.exists(UPLOAD_FOLDER) else 'Não existe'}")
    print(f"Verificando permissões da pasta de uploads: {'Gravável' if os.access(UPLOAD_FOLDER, os.W_OK) else 'Não gravável'}")
    print(f"Verificando variáveis de ambiente:")
    print(f"  PINATA_API_KEY: {'Configurada' if os.getenv('PINATA_API_KEY') else 'Não configurada'}")
    print(f"  PINATA_SECRET_KEY: {'Configurada' if os.getenv('PINATA_SECRET_KEY') else 'Não configurada'}")
    print(f"  OPENAI_API_KEY: {'Configurada' if os.getenv('OPENAI_API_KEY') else 'Não configurada'}")
    # 20250527
    app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
