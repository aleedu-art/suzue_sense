# NFT Minter com Análise de Sentimentos por IA

Este projeto é uma aplicação web completa para criação e mintagem de NFTs com análise de sentimentos baseada em IA. A aplicação permite fazer upload de imagens para o IPFS via Pinata, analisar automaticamente as imagens com a API OpenAI para extrair sentimentos, psicologia das cores, signos e linguagem visual, criar metadados enriquecidos e mintar NFTs em contratos ERC-721.

## Funcionalidades

- **Upload de imagens para IPFS** via Pinata
- **Análise de sentimentos com IA** usando a API OpenAI (GPT-4 Vision)
- **Geração automática de metadados enriquecidos** com análise de sentimentos
- **Criação de metadados no formato ERC-721** e upload para IPFS
- **Mintagem de NFTs** em contratos ERC-721 compatíveis
- **Interface responsiva** para desktop e dispositivos móveis
- **Integração com MetaMask** para conectar carteiras e assinar transações
- **Suporte a diferentes redes blockchain** (Ethereum, Polygon, etc.)
- **Fluxo integrado** de criação de metadados e mintagem em uma única ação


2. **Análise de Imagem**:
   - O hash IPFS é usado para criar uma URL da imagem
   - A URL é enviada para a API OpenAI (GPT-4 Vision)
   - A API analisa a imagem e retorna informações sobre sentimentos, cores, signos e linguagem visual
   - A análise é processada e estruturada para uso nos metadados

3. **Criação de Metadados**:
   - Os metadados são criados no formato ERC-721
   - A descrição é enriquecida com a análise de sentimentos
   - Atributos são gerados com base na análise
   - Os metadados são enviados para o Pinata
   - O hash IPFS dos metadados é retornado

4. **Mintagem de NFT**:
   - O hash IPFS dos metadados é usado como tokenURI
   - A carteira MetaMask é usada para assinar a transação
   - O NFT é mintado no contrato ERC-721 especificado
   - O hash da transação é retornado e exibido na interface

