document.getElementById('showInputBtn').addEventListener('click', () => {
    const inputContainer = document.getElementById('inputContainer');
    if (inputContainer.style.display === 'none') {
        inputContainer.style.display = 'block'; // Mostra o input
    } else {
        inputContainer.style.display = 'none'; // Esconde o input
    }
});

document.getElementById("saveBioBtn").addEventListener("click", function() {
    const newBio = document.getElementById("bioInput").value.trim();
    
    if (newBio) {
        const userId = document.getElementById("user_id").value; // Pega o ID do usuário do campo hidden
        const apiUrl = `http://localhost:5000/files/username/${userId}/bio`; // URL da API

        // Enviar a requisição PUT para a API
        fetch(apiUrl, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ new_bio: newBio })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Bio atualizada com sucesso") {
                // Atualiza a bio exibida na página
                document.querySelector(".bio-user").textContent = newBio;
                alert("Bio atualizada com sucesso!");
            } else {
                alert("Erro ao atualizar a bio");
            }
        })
        .catch(error => {
            console.error("Erro:", error);
            alert("Erro na requisição. Tente novamente.");
        });
    } else {
        alert("A bio não pode estar vazia!");
    }
});

function handleImageClick(element) {
  // Garantir que `element` seja válido e obtenha o atributo src
  const imageUrl = element.getAttribute('src');

  // Criar o modal
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
    align-items: center; z-index: 1000;
  `;

  const img = document.createElement('img');
  img.src = imageUrl;
  img.style.cssText = 'max-width: 93%; max-height: 93%; border-radius: 8px;';

  const closeButton = document.createElement('span');
  closeButton.textContent = 'X';
  closeButton.style.cssText = `
    position: absolute; top: 20px; right: 20px; color: white;
    font-size: 24px; cursor: pointer;
  `;
  closeButton.onclick = () => document.body.removeChild(modal);

  modal.appendChild(img);
  modal.appendChild(closeButton);
  document.body.appendChild(modal);
}


function displayFileName() {
    const fileInput = document.getElementById('files');
    const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : 'Nenhum arquivo escolhido';
    document.getElementById('file-name').textContent = fileName;
  }



  // função envio de img para o banco de dados foto perfil
  function uploadImage(event) {
    const fileInput = event.target; // O campo de input do tipo file
    const file = fileInput.files[0]; // Obtém o arquivo selecionado
  
    // Verifique se um arquivo foi selecionado
    if (!file) {
      alert("Por favor, selecione uma imagem.");
      return;
    }
  
    // Obtém o ID do usuário a partir do campo hidden
    const userId = document.getElementById('id_usuario') ? document.getElementById('id_usuario').value : null;
  
    
  
    if (!userId) {
      alert("ID do usuário não encontrado.");
      return;
    }
  
    // Crie um objeto FormData para enviar o arquivo
    const formData = new FormData();
    formData.append("file", file);
  
    // Envie a imagem para o servidor usando fetch
    fetch(`http://localhost:5000/files/uploadfile/${userId}`, {
      method: 'POST',
      headers: {
        'accept': 'application/json',
      },
      body: formData,
    })
    .then(response => response.json()) 
    .then(data => {
      
      
    })
    
  }
  


  function uploadImageBanner(event) {
    const fileInput = event.target;
    const file = fileInput.files[0];

    if (!file) {
        alert("Por favor, selecione uma imagem.");
        return;
    }

    const userId = document.getElementById('id_usuario')?.value;

    if (!userId) {
        alert("ID do usuário não encontrado.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);  // Nome da chave deve ser "file"

    fetch(`http://localhost:5000/files/banner/uploadfile/${userId}`, {
      method: 'POST',
      headers: {
          'accept': 'application/json',
      },
      body: formData,
  })
  
   
}
