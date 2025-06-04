/**
 * Visualizador de NFTs para BNB Smart Chain Testnet usando Moralis API v2
 * Versão simplificada com foco em compatibilidade máxima
 * Versão 6: Layout aprimorado com formatação de descrição
 */

// Configuração da API Moralis
//const MORALIS_API_KEY = "INSIRA_SUA_API_KEY_AQUI"; // Substitua pela sua API key do Moralis
//const MORALIS_API_KEY = process.env.MORALIS_API_KEY;
//const MORALIS_API_KEY = const MORALIS_API_KEY = process.env.MORALIS_API_KEY || ""; // Substitua pela sua API key do Moralis
const MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjVlYTk4NWU0LTUzZDMtNDA2Yy05ZmMxLTBlODk3NjMwOWQxNyIsIm9yZ0lkIjoiNDQ5MzU0IiwidXNlcklkIjoiNDYyMzQwIiwidHlwZUlkIjoiMTk2MDdiMjUtNDM0Yi00M2Q2LTljNmUtNzcyNjVmN2UwYjNlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDgyOTUyMjMsImV4cCI6NDkwNDA1NTIyM30.KwwtCbfsIYg-L3nytcZ7tYCXHIiHxfupXsnYGbwtSH0" ; // Substitua pela sua API key do Moralis

 
const BNB_TESTNET_CHAIN_ID = ["0x61", "97"]; // Chain ID da BNB Smart Chain Testnet (hex e decimal)
const BNB_TESTNET_CHAIN_NAME = "bsc testnet"; // Nome da chain para a API Moralis v2
const BSCSCAN_TESTNET_URL = "https://testnet.bscscan.com";
const OPENSEA_TESTNET_URL = "https://testnets.opensea.io";

// Variáveis globais
let currentAccount = null;
let currentChainId = null;
let nftsCache = [];

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log("Aplicação inicializada");
    
    // Configurar event listeners
    document.getElementById('connect-wallet-btn').addEventListener('click', connectWallet);
    document.getElementById('fetch-nfts-btn').addEventListener('click', fetchNFTs);
    document.getElementById('toggle-metadata-btn').addEventListener('click', toggleMetadataSection);
    
    // Verificar se MetaMask está instalado
    if (typeof window.ethereum !== 'undefined') {
        console.log("MetaMask detectado");
        checkConnection();
        setupMetaMaskListeners();
    } else {
        console.log("MetaMask não detectado");
        showAlert("MetaMask não encontrado. Por favor, instale a extensão MetaMask para usar este aplicativo.", "warning");
        document.getElementById('connect-wallet-btn').disabled = true;
    }
});

/**
 * Configura listeners para eventos da MetaMask
 */
function setupMetaMaskListeners() {
    if (window.ethereum) {
        window.ethereum.on('accountsChanged', function(accounts) {
            console.log("Contas alteradas:", accounts);
            if (accounts.length === 0) {
                disconnectWallet();
            } else {
                currentAccount = accounts[0];
                updateWalletInfo();
            }
        });
        
        window.ethereum.on('chainChanged', function(chainId) {
            console.log("Rede alterada:", chainId);
            currentChainId = chainId;
            updateNetworkInfo();
            window.location.reload();
        });
    }
}

/**
 * Verifica se já existe uma conexão com a MetaMask
 */
async function checkConnection() {
    try {
        if (window.ethereum) {
            const accounts = await window.ethereum.request({ method: 'eth_accounts' });
            if (accounts.length > 0) {
                currentAccount = accounts[0];
                console.log("Já conectado à conta:", currentAccount);
                
                currentChainId = await window.ethereum.request({ method: 'eth_chainId' });
                console.log("Chain ID atual:", currentChainId);
                
                updateWalletInfo();
                updateNetworkInfo();
                checkCorrectNetwork();
            }
        }
    } catch (error) {
        console.error("Erro ao verificar conexão:", error);
    }
}

/**
 * Conecta à carteira MetaMask
 */
async function connectWallet() {
    console.log("Tentando conectar à carteira...");
    
    try {
        if (window.ethereum) {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            currentAccount = accounts[0];
            console.log("Conectado à conta:", currentAccount);
            
            currentChainId = await window.ethereum.request({ method: 'eth_chainId' });
            console.log("Chain ID atual:", currentChainId, "Tipo:", typeof currentChainId);
            
            updateWalletInfo();
            updateNetworkInfo();
            checkCorrectNetwork();
            
            showAlert("Carteira conectada com sucesso!", "success");
        } else {
            showAlert("MetaMask não encontrado. Por favor, instale a extensão MetaMask.", "warning");
        }
    } catch (error) {
        console.error("Erro ao conectar carteira:", error);
        showAlert("Erro ao conectar à MetaMask: " + (error.message || "Verifique se a extensão está desbloqueada."), "danger");
    }
}

/**
 * Desconecta a carteira (limpa a interface)
 */
function disconnectWallet() {
    currentAccount = null;
    document.getElementById('wallet-status').textContent = "Desconectado";
    document.getElementById('wallet-status').className = "badge bg-secondary";
    document.getElementById('wallet-address').textContent = "Não conectado";
    document.getElementById('wallet-balance').textContent = "0 BNB";
    document.getElementById('fetch-nfts-btn').disabled = true;
    
    document.getElementById('nfts-grid').innerHTML = '';
    document.getElementById('no-nfts-message').style.display = 'block';
    
    console.log("Carteira desconectada");
}

/**
 * Atualiza as informações da carteira na interface
 */
async function updateWalletInfo() {
    if (!currentAccount) return;
    
    document.getElementById('wallet-status').textContent = "Conectado";
    document.getElementById('wallet-status').className = "badge bg-success";
    document.getElementById('wallet-address').textContent = formatAddress(currentAccount);
    document.getElementById('fetch-nfts-btn').disabled = false;
    
    try {
        if (window.ethereum) {
            const balance = await window.ethereum.request({
                method: 'eth_getBalance',
                params: [currentAccount, 'latest']
            });
            
            // Converter de wei para ether
            const balanceInEth = parseInt(balance, 16) / 1e18;
            document.getElementById('wallet-balance').textContent = `${balanceInEth.toFixed(4)} BNB`;
        }
    } catch (error) {
        console.error("Erro ao obter saldo:", error);
        document.getElementById('wallet-balance').textContent = "Erro ao carregar";
    }
}

/**
 * Verifica se um chainId corresponde à BNB Testnet
 * @param {string} chainId - Chain ID para verificar
 * @returns {boolean} - true se for BNB Testnet, false caso contrário
 */
function isBNBTestnet(chainId) {
    if (!chainId) return false;
    
    // Converter para string para garantir comparação correta
    const chainIdStr = String(chainId);
    console.log("Verificando chainId:", chainIdStr);
    
    // Verificar diretamente se está na lista
    if (BNB_TESTNET_CHAIN_ID.includes(chainIdStr)) {
        console.log("Chain ID encontrado diretamente na lista");
        return true;
    }
    
    // Tentar converter de hex para decimal e verificar
    if (chainIdStr.startsWith('0x')) {
        const decimal = parseInt(chainIdStr, 16).toString();
        console.log("Convertido de hex para decimal:", decimal);
        if (BNB_TESTNET_CHAIN_ID.includes(decimal)) {
            console.log("Chain ID encontrado após conversão hex->decimal");
            return true;
        }
    } 
    // Tentar converter de decimal para hex e verificar
    else {
        try {
            const hex = '0x' + parseInt(chainIdStr).toString(16);
            console.log("Convertido de decimal para hex:", hex);
            if (BNB_TESTNET_CHAIN_ID.includes(hex)) {
                console.log("Chain ID encontrado após conversão decimal->hex");
                return true;
            }
        } catch (e) {
            console.error("Erro ao converter chainId:", e);
        }
    }
    
    return false;
}

/**
 * Atualiza as informações da rede na interface
 */
function updateNetworkInfo() {
    if (!currentChainId) return;
    
    console.log("Atualizando informações da rede. Chain ID atual:", currentChainId);
    
    // Verificar se está na BNB Testnet
    if (isBNBTestnet(currentChainId)) {
        document.getElementById('network-name').textContent = "BNB Smart Chain Testnet";
        document.getElementById('network-badge').style.display = "inline";
    } else {
        // Tentar exibir em formato decimal para melhor compreensão
        let chainIdDecimal;
        try {
            const chainIdStr = String(currentChainId);
            chainIdDecimal = chainIdStr.startsWith('0x') ? 
                parseInt(chainIdStr, 16) : parseInt(chainIdStr);
        } catch (e) {
            chainIdDecimal = currentChainId;
        }
        document.getElementById('network-name').textContent = `ID da Rede: ${chainIdDecimal}`;
        document.getElementById('network-badge').style.display = "none";
    }
}

/**
 * Verifica se está na rede correta (BNB Testnet) e sugere mudar se necessário
 */
async function checkCorrectNetwork() {
    console.log("Verificando se está na rede correta...");
    
    if (!isBNBTestnet(currentChainId)) {
        console.log("Rede incorreta. Solicitando mudança para BNB Testnet");
        showAlert("Você não está na BNB Smart Chain Testnet. Clique em 'Mudar Rede' para continuar.", "warning", true);
    } else {
        console.log("Rede correta detectada: BNB Smart Chain Testnet");
        // Limpar alertas anteriores sobre rede incorreta
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (alert.textContent.includes("BNB Smart Chain Testnet")) {
                alert.remove();
            }
        });
    }
}

/**
 * Solicita mudança para a rede BNB Testnet
 */
async function switchToBNBTestnet() {
    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: "0x61" }],
        });
    } catch (switchError) {
        if (switchError.code === 4902) {
            try {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: "0x61",
                        chainName: 'BNB Smart Chain Testnet',
                        nativeCurrency: {
                            name: 'tBNB',
                            symbol: 'tBNB',
                            decimals: 18
                        },
                        rpcUrls: ['https://data-seed-prebsc-1-s1.binance.org:8545/'],
                        blockExplorerUrls: [BSCSCAN_TESTNET_URL]
                    }],
                });
            } catch (addError) {
                console.error("Erro ao adicionar rede:", addError);
                showAlert("Erro ao adicionar rede: " + (addError.message || "Erro desconhecido"), "danger");
            }
        } else {
            console.error("Erro ao mudar de rede:", switchError);
            showAlert("Erro ao mudar de rede: " + (switchError.message || "Erro desconhecido"), "danger");
        }
    }
}

/**
 * Busca NFTs da carteira conectada usando a API REST Moralis v2
 */
async function fetchNFTs() {
    if (!currentAccount) {
        showAlert("Por favor, conecte sua carteira primeiro.", "warning");
        return;
    }
    
    if (!isBNBTestnet(currentChainId)) {
        showAlert("Por favor, mude para a rede BNB Smart Chain Testnet para continuar.", "warning");
        return;
    }
    
    if (MORALIS_API_KEY === "INSIRA_SUA_API_KEY_AQUI") {
        showAlert("Por favor, configure sua API key do Moralis no arquivo app_v6.js", "danger");
        console.error("API key do Moralis não configurada");
        return;
    }
    
    // Mostrar loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('nfts-grid').innerHTML = '';
    document.getElementById('no-nfts-message').style.display = 'none';
    
    try {
        // Configurar parâmetros para a API
        const chain = document.getElementById('chain-select').value;
        const address = currentAccount;
        const contractAddress = document.getElementById('contract-address').value.trim();
        
        console.log(`Buscando NFTs para endereço ${address} na rede ${chain}`);
        
        // Construir URL da API
        let apiUrl = `https://deep-index.moralis.io/api/v2/${address}/nft?chain=${encodeURIComponent(chain)}&format=decimal&normalizeMetadata=true`;
        
        // Adicionar endereço do contrato se fornecido
        if (contractAddress) {
            apiUrl += `&token_addresses=${contractAddress}`;
        }
        
        console.log("URL da API:", apiUrl);
        
        // Fazer requisição à API Moralis v2
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'X-API-Key': MORALIS_API_KEY
            }
        });
        
        // Verificar se a resposta foi bem-sucedida
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Erro na API Moralis: ${errorData.message || response.statusText || response.status}`);
        }
        
        // Processar resposta
        const data = await response.json();
        console.log("Resposta da API Moralis:", data);
        
        // Armazenar NFTs no cache e exibir
        nftsCache = data.result || [];
        displayNFTs(nftsCache);
    } catch (error) {
        console.error("Erro ao buscar NFTs:", error);
        showAlert(`Erro ao buscar NFTs: ${error.message}`, "danger");
        document.getElementById('loading').style.display = 'none';
        document.getElementById('no-nfts-message').style.display = 'block';
    }
}

/**
 * Exibe os NFTs na interface
 * @param {Array} nfts - Array de NFTs retornados pela API Moralis
 */
function displayNFTs(nfts) {
    // Ocultar loading
    document.getElementById('loading').style.display = 'none';
    
    // Verificar se há NFTs para exibir
    if (!nfts || nfts.length === 0) {
        document.getElementById('no-nfts-message').style.display = 'block';
        return;
    }
    
    // Limpar grid e exibir NFTs
    const nftsGrid = document.getElementById('nfts-grid');
    nftsGrid.innerHTML = '';
    
    nfts.forEach((nft, index) => {
        // Processar metadados
        let metadata = null;
        let name = `NFT #${nft.token_id}`;
        let description = 'Sem descrição disponível';
        let image = '';
        let attributes = [];
        
        try {
            if (nft.normalized_metadata) {
                metadata = nft.normalized_metadata;
                name = metadata.name || name;
                description = metadata.description || description;
                
                // Processar URL da imagem
                if (metadata.image) {
                    image = processImageUrl(metadata.image);
                }
                
                // Processar atributos
                if (metadata.attributes) {
                    attributes = metadata.attributes;
                }
            } else if (nft.metadata) {
                // Tentar parsear metadados se não estiverem normalizados
                try {
                    const parsedMetadata = JSON.parse(nft.metadata);
                    metadata = parsedMetadata;
                    name = parsedMetadata.name || name;
                    description = parsedMetadata.description || description;
                    
                    if (parsedMetadata.image) {
                        image = processImageUrl(parsedMetadata.image);
                    }
                    
                    if (parsedMetadata.attributes) {
                        attributes = parsedMetadata.attributes;
                    }
                } catch (parseError) {
                    console.warn("Erro ao parsear metadados:", parseError);
                }
            }
        } catch (error) {
            console.error("Erro ao processar metadados:", error);
        }
        
        // Criar card para o NFT
        const nftCard = document.createElement('div');
        nftCard.className = 'col';
        nftCard.innerHTML = `
           <div class="nft-card">
               
           
                <div class="nft-image-container">
                    ${image ? `<img src="${image}" class="nft-image" alt="${name}" onerror="this.onerror=null; this.src=''; this.parentElement.innerHTML='<div class=\\'nft-placeholder\\'><i class=\\'fas fa-image\\'></i></div>';">` : 
                    `<div class="nft-placeholder"><i class="fas fa-image"></i></div>`}
                    <div class="network-badge">BNB Testnet</div>
                </div>
                <div class="nft-body">
                    <h5 class="nft-title">${escapeHtml(name)}</h5>
                    <p class="nft-description">${escapeHtml(getShortDescription(description))}</p>
                    <div class="nft-footer">
                        <span class="nft-id">ID: ${nft.token_id}</span>
                        <a href="#" class="nft-link view-details" data-index="${index}">Ver detalhes</a>
                    </div>
                </div>
            </div>
        `;
        
        nftsGrid.appendChild(nftCard);
        
        // Adicionar evento para visualizar detalhes
        nftCard.querySelector('.view-details').addEventListener('click', (e) => {
            e.preventDefault();
            showNFTDetails(nfts[index]);
        });
    });
}

/**
 * Obtém uma versão curta da descrição para exibir no card
 * @param {string} description - Descrição completa
 * @returns {string} - Versão curta da descrição
 */
function getShortDescription(description) {
    if (!description) return '';
    
    // Verificar se a descrição contém marcadores de análise
    if (description.includes('**Análise de Sentimentos:**')) {
        // Extrair apenas a parte inicial antes da análise
        const parts = description.split('**Análise de Sentimentos:**');
        return parts[0].trim();
    }
    
    // Limitar a 150 caracteres se não tiver marcadores
    if (description.length > 150) {
        return description.substring(0, 147) + '...';
    }
    
    return description;
}

/**
 * Formata a descrição para exibir no modal com seções separadas
 * @param {string} description - Descrição completa
 * @returns {string} - HTML formatado com seções separadas
 */
function formatDescriptionWithSections(description) {
    if (!description) return '<p>Sem descrição disponível</p>';
    
    // Verificar se a descrição contém marcadores de análise
    const hasAnalysis = description.includes('**Análise de Sentimentos:**');
    
    if (!hasAnalysis) {
        // Se não tiver marcadores, retornar a descrição original
        return `<p>${escapeHtml(description)}</p>`;
    }
    
    // Extrair a parte inicial (antes da análise)
    let formattedHtml = '';
    const parts = description.split('**Análise de Sentimentos:**');
    
    if (parts[0].trim()) {
        formattedHtml += `<p>${escapeHtml(parts[0].trim())}</p>`;
    }
    
    // Processar as seções de análise
    const sections = [
        { marker: '**Análise de Sentimentos:**', title: 'Análise de Sentimentos' },
        { marker: '**Psicologia das Cores:**', title: 'Psicologia das Cores' },
        { marker: '**Relação com Signos:**', title: 'Relação com Signos' },
        { marker: '**Linguagem Visual:**', title: 'Linguagem Visual' }
    ];
    
    // Reconstruir o texto após o primeiro marcador
    let remainingText = '**Análise de Sentimentos:**' + parts[1];
    
    // Processar cada seção
    sections.forEach((section, index) => {
        if (remainingText.includes(section.marker)) {
            const sectionParts = remainingText.split(section.marker);
            
            // Se não for a primeira seção, pegar o conteúdo da seção anterior
            if (index > 0) {
                const sectionContent = sectionParts[0].trim();
                formattedHtml += `
                    <div class="analysis-item">
                        <div class="analysis-title">${sections[index-1].title}</div>
                        <div class="analysis-content">${escapeHtml(sectionContent)}</div>
                    </div>
                `;
            }
            
            // Atualizar o texto restante
            remainingText = section.marker + sectionParts[1];
            
            // Se for a última seção, adicionar seu conteúdo também
            if (index === sections.length - 1) {
                const sectionContent = sectionParts[1].trim();
                formattedHtml += `
                    <div class="analysis-item">
                        <div class="analysis-title">${section.title}</div>
                        <div class="analysis-content">${escapeHtml(sectionContent)}</div>
                    </div>
                `;
            }
        }
    });
    
    return formattedHtml;
}

/**
 * Exibe os detalhes de um NFT específico em um modal
 * @param {Object} nft - Objeto NFT retornado pela API Moralis
 */
function showNFTDetails(nft) {
    console.log("Exibindo detalhes do NFT:", nft);
    
    // Processar metadados
    let metadata = null;
    let name = `NFT #${nft.token_id}`;
    let description = 'Sem descrição disponível';
    let image = '';
    let attributes = [];
    
    try {
        if (nft.normalized_metadata) {
            metadata = nft.normalized_metadata;
            name = metadata.name || name;
            description = metadata.description || description;
            
            // Processar URL da imagem
            if (metadata.image) {
                image = processImageUrl(metadata.image);
            }
            
            // Processar atributos
            if (metadata.attributes) {
                attributes = metadata.attributes;
            }
        } else if (nft.metadata) {
            // Tentar parsear metadados se não estiverem normalizados
            try {
                const parsedMetadata = JSON.parse(nft.metadata);
                metadata = parsedMetadata;
                name = parsedMetadata.name || name;
                description = parsedMetadata.description || description;
                
                if (parsedMetadata.image) {
                    image = processImageUrl(parsedMetadata.image);
                }
                
                if (parsedMetadata.attributes) {
                    attributes = parsedMetadata.attributes;
                }
            } catch (parseError) {
                console.warn("Erro ao parsear metadados para modal:", parseError);
            }
        }
    } catch (error) {
        console.error("Erro ao processar metadados para modal:", error);
    }
    
    // Preencher o modal com os detalhes do NFT
    document.getElementById('modal-nft-name').textContent = name;
    
    // Formatar a descrição com seções
    const descriptionContainer = document.getElementById('modal-nft-description');
    descriptionContainer.innerHTML = formatDescriptionWithSections(description);
    
    document.getElementById('modal-nft-id').textContent = nft.token_id;
    document.getElementById('modal-nft-contract').textContent = formatAddress(nft.token_address);
    document.getElementById('modal-nft-owner').textContent = formatAddress(currentAccount);
    
    // Configurar imagem
    const modalImage = document.getElementById('modal-nft-image');
    if (image) {
        modalImage.src = image;
        modalImage.style.display = 'block';
        
        // Adicionar handler para erro de carregamento da imagem
        modalImage.onerror = function() {
            this.onerror = null;
            this.style.display = 'none';
            this.parentElement.innerHTML = '<div class="nft-placeholder" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"><i class="fas fa-image"></i></div>';
        };
    } else {
        modalImage.style.display = 'none';
        modalImage.parentElement.innerHTML = '<div class="nft-placeholder" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"><i class="fas fa-image"></i></div>';
    }
    
    // Configurar links
    document.getElementById('modal-contract-link').href = `${BSCSCAN_TESTNET_URL}/token/${nft.token_address}`;
    document.getElementById('modal-owner-link').href = `${BSCSCAN_TESTNET_URL}/address/${currentAccount}`;
    document.getElementById('modal-bscscan-link').href = `${BSCSCAN_TESTNET_URL}/token/${nft.token_address}?a=${nft.token_id}`;
    document.getElementById('modal-opensea-link').href = `${OPENSEA_TESTNET_URL}/assets/bsc-testnet/${nft.token_address}/${nft.token_id}`;
    
    // Configurar atributos
    const attributesContainer = document.getElementById('modal-attributes');
    attributesContainer.innerHTML = '';
    
    if (attributes && attributes.length > 0) {
        document.getElementById('modal-attributes-container').style.display = 'block';
        
        attributes.forEach(attr => {
            const attrElement = document.createElement('div');
            attrElement.className = 'attribute-badge';
            
            // Verificar formato do atributo (pode variar entre coleções)
            if (attr.trait_type && attr.value !== undefined) {
                attrElement.innerHTML = `<strong>${attr.trait_type}:</strong> ${attr.value}`;
            } else if (typeof attr === 'object') {
                const key = Object.keys(attr)[0];
                attrElement.innerHTML = `<strong>${key}:</strong> ${attr[key]}`;
            }
            
            attributesContainer.appendChild(attrElement);
        });
    } else {
        document.getElementById('modal-attributes-container').style.display = 'none';
    }
    
    // Configurar metadados JSON
    const metadataJson = document.getElementById('modal-metadata-json');
    if (metadata) {
        metadataJson.textContent = JSON.stringify(metadata, null, 2);
    } else {
        metadataJson.textContent = "Metadados não disponíveis";
    }
    
    // Resetar visibilidade da seção de metadados
    document.getElementById('metadata-json-container').style.display = 'none';
    document.getElementById('toggle-metadata-btn').textContent = 'Mostrar Metadados';
    
    // Exibir o modal
    const modal = new bootstrap.Modal(document.getElementById('nftDetailModal'));
    modal.show();
}

/**
 * Alterna a visibilidade da seção de metadados no modal
 */
function toggleMetadataSection() {
    const metadataContainer = document.getElementById('metadata-json-container');
    const toggleBtn = document.getElementById('toggle-metadata-btn');
    
    if (metadataContainer.style.display === 'none') {
        metadataContainer.style.display = 'block';
        toggleBtn.textContent = 'Ocultar Metadados';
    } else {
        metadataContainer.style.display = 'none';
        toggleBtn.textContent = 'Mostrar Metadados';
    }
}

/**
 * Processa a URL da imagem para garantir que seja acessível
 * @param {string} imageUrl - URL da imagem do NFT
 * @returns {string} URL processada
 */
function processImageUrl(imageUrl) {
    if (!imageUrl) return '';
    
    // Substituir ipfs:// por gateway público
    if (imageUrl.startsWith('ipfs://')) {
        return imageUrl.replace('ipfs://', 'https://ipfs.io/ipfs/');
    }
    
    // Adicionar https:// se necessário
    if (imageUrl.startsWith('//')) {
        return 'https:' + imageUrl;
    }
    
    return imageUrl;
}

/**
 * Formata um endereço Ethereum para exibição (abrevia o meio)
 * @param {string} address - Endereço completo
 * @returns {string} Endereço abreviado
 */
function formatAddress(address) {
    if (!address) return '';
    return address.substring(0, 6) + '...' + address.substring(address.length - 4);
}

/**
 * Escapa caracteres HTML para evitar XSS
 * @param {string} unsafe - String não segura
 * @returns {string} String escapada
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Exibe um alerta na interface
 * @param {string} message - Mensagem do alerta
 * @param {string} type - Tipo do alerta (success, danger, warning, info)
 * @param {boolean} withAction - Se deve incluir botão de ação
 */
function showAlert(message, type = 'info', withAction = false) {
    const alertsContainer = document.getElementById('alerts-container');
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            ${withAction ? `<button class="btn btn-sm btn-outline-${type} ms-3" id="${alertId}-action">Mudar Rede</button>` : ''}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        </div>
    `;
    
    alertsContainer.innerHTML += alertHtml;
    
    // Adicionar evento ao botão de ação se existir
    if (withAction) {
        document.getElementById(`${alertId}-action`).addEventListener('click', switchToBNBTestnet);
    }
    
    // Auto-remover após 10 segundos
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            alertElement.remove();
        }
    }, 10000);
}
