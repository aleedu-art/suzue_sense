# Visualizador de NFTs para BNB Smart Chain Testnet

Este projeto é um visualizador de NFTs que permite aos usuários conectar suas carteiras MetaMask e visualizar os NFTs que possuem na rede BNB Smart Chain Testnet. A aplicação utiliza a API Moralis v2 para buscar e exibir informações detalhadas sobre os NFTs.

## Índice

1. [Requisitos](#requisitos)
2. [Configuração](#configuração)
3. [Como Usar](#como-usar)
4. [Funcionalidades](#funcionalidades)
5. [Opções de Hospedagem](#opções-de-hospedagem)
6. [Solução de Problemas](#solução-de-problemas)
7. [Personalização](#personalização)


### 3. Configurar a MetaMask para BNB Smart Chain Testnet

Se você ainda não configurou a MetaMask para a BNB Smart Chain Testnet:

1. Abra a extensão MetaMask
2. Clique no menu de redes (geralmente mostra "Ethereum Mainnet")
3. Clique em "Adicionar rede"
4. Preencha com os seguintes dados:
   - Nome da Rede: BNB Smart Chain Testnet
   - URL do RPC: https://data-seed-prebsc-1-s1.binance.org:8545/
   - ID da Cadeia: 97
   - Símbolo da Moeda: tBNB
   - URL do Explorador: https://testnet.bscscan.com

5. Obtenha tBNB de teste no [faucet oficial](https://testnet.bnbchain.org/faucet-smart)

## Como Usar

1. Abra o arquivo `index_v2.html` no seu navegador
2. Clique no botão "Conectar MetaMask"
3. Autorize a conexão na janela pop-up da MetaMask
4. Verifique se você está na rede BNB Smart Chain Testnet
   - Se não estiver, a aplicação oferecerá a opção de mudar automaticamente
5. Opcionalmente, insira o endereço do contrato NFT específico que deseja visualizar
6. Clique em "Buscar NFTs"
7. Os NFTs encontrados serão exibidos em cards
8. Clique em "Ver detalhes" em qualquer NFT para ver informações completas

## Funcionalidades

- **Conexão com MetaMask**: Conecte-se facilmente à sua carteira
- **Detecção de Rede**: Verifica automaticamente se você está na BNB Testnet
- **Busca de NFTs**: Visualize todos os NFTs da sua carteira ou de um contrato específico
- **Visualização Detalhada**: Veja imagens, metadados e atributos de cada NFT
- **Links Externos**: Acesse facilmente o NFT no BscScan e OpenSea Testnet
- **Visualização de Metadados**: Examine os metadados completos em formato JSON
- **Interface Responsiva**: Funciona em dispositivos móveis e desktop





### NFTs Não Aparecem

- Verifique se você está conectado à rede BNB Smart Chain Testnet
- Confirme se a carteira conectada possui NFTs nessa rede
- Verifique se a API key do Moralis está correta e ativa
- Abra o console do navegador (F12) para ver mensagens de erro detalhadas

### Problemas de Conexão com MetaMask

- Certifique-se de que a MetaMask está instalada e desbloqueada
- Tente atualizar a página e reconectar
- Verifique se você tem permissões para conectar sites à MetaMask

### Imagens de NFT Não Carregam

- Alguns NFTs podem usar gateways IPFS que estão offline
- A aplicação tenta converter URLs IPFS para gateways públicos, mas nem sempre funciona
- Verifique o console para ver a URL da imagem que está tentando carregar



