function handleImageClick(element) {
    // Obter o link da imagem a partir do atributo data-src
    const imageUrl = element.getAttribute('data-src');
    
    // Verificar se a URL da imagem é válida
    if (!imageUrl) {
      console.error('A URL da imagem não foi encontrada.');
      return;
    }
  
    // Criar o modal
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background-color: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
      align-items: center; z-index: 1000;
      borrde-radius: 50% ;
    `;
  
    // Criar a imagem para o modal
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.cssText = 'max-width: 93%; max-height: 93%; border-radius: 8px;';
    img.alt = 'Imagem ampliada';  // Adicionar texto alternativo para acessibilidade
  
    // Criar o botão de fechar
    const closeButton = document.createElement('span');
    closeButton.textContent = 'X';
    closeButton.style.cssText = `
      position: absolute; top: 20px; right: 20px; color: white;
      font-size: 24px; cursor: pointer;
    `;
    closeButton.onclick = () => document.body.removeChild(modal);



  
    // Modal na lupa de pesquisar 
    // Adicionar a imagem e o botão de fechar ao modal
    modal.appendChild(img);
    modal.appendChild(closeButton);
  
    // Adicionar o modal à página
    document.body.appendChild(modal);
  }
  
 const modalContainer = document.getElementById('modal-container');
    const openButton = document.getElementById('open');

    // Abrir o modal ao clicar no botão
    openButton.addEventListener('click', () => {
      modalContainer.classList.add('active');
    });

    // Fechar o modal ao clicar fora dele
    modalContainer.addEventListener('click', (event) => {
      if (event.target === modalContainer) {
        modalContainer.classList.remove('active');
      }
    });









// Modal na lupa de pesquisar 




const searchInput = document.getElementById('search');
const searchResults = document.getElementById('search-results');

// Abrir o modal ao clicar no botão
openButton.addEventListener('click', () => {
  modalContainer.classList.add('active');
});

// Fechar o modal ao clicar fora dele
modalContainer.addEventListener('click', (event) => {
  if (event.target === modalContainer) {
    modalContainer.classList.remove('active');
  }
});

// Enviar a pesquisa para o backend
searchInput.addEventListener('input', async (e) => {
  const query = e.target.value;

  // Limpar os resultados se o input tiver menos de 3 caracteres
  if (query.length < 3) {
    searchResults.innerHTML = '<div class="p-4 text-center text-gray-500 italic">Digite pelo menos 3 caracteres para pesquisar.</div>';
    return;
  }

  try {
    const response = await fetch('/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error('Erro ao buscar dados');
    }

    const data = await response.json();

    // Limpar resultados anteriores
    searchResults.innerHTML = '';

    if (data.results && data.results.length > 0) {
      // Exibir resultados como links estilizados
      data.results.forEach((result) => {
        const resultElement = document.createElement('a');
        resultElement.href = `/devorbit/perfil/${result.user_id}/`; // Corrige para a URL no formato esperado
        resultElement.target = '_blank';
        resultElement.classList.add(
          'flex', 'flex-col', 'items-start', 'p-4', 'mb-4',
          'bg-white', 'shadow-lg', 'rounded-lg', 'border', 'border-gray-200',
          'hover:bg-gray-100', 'transition-all', 'duration-200'
        );

        // Adicionar título e conteúdo do post
        const title = document.createElement('h3');
        title.classList.add('text-lg', 'font-bold', 'text-gray-800', 'mb-2');
        title.textContent = result.title;

        const content = document.createElement('p');
        content.classList.add('text-sm', 'text-gray-700', 'leading-relaxed');
        content.textContent = result.resulm;

        const author = document.createElement('span');
        author.classList.add('text-xs', 'text-gray-500', 'mt-2');
        author.textContent = `Criado por: @${result.username} | Likes: ${result.likes}`;

        // Adicionar os elementos ao link
        resultElement.appendChild(title);
        resultElement.appendChild(content);
        resultElement.appendChild(author);

        searchResults.appendChild(resultElement);
      });
      
    } else {
      // Exibir mensagem de "nenhum resultado encontrado"
      const noResultElement = document.createElement('div');
      noResultElement.classList.add('p-4', 'text-center', 'text-gray-500', 'italic');
      noResultElement.textContent = 'Nenhum resultado encontrado.';
      searchResults.appendChild(noResultElement);
    }
  } catch (error) {
    console.error('Erro ao realizar a pesquisa:', error);
  }
});
