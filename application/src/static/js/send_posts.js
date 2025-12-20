// in page posts.html

document.addEventListener("DOMContentLoaded", function () {
    function creatnewPOst(event) {
      event.preventDefault();
      const user_id = document.getElementById("id_user").value;
      const nome = document.getElementById("nome").value;
      const titulo = document.getElementById("titulo").value;
      const post = document.getElementById("post").value;
      const fileInput = document.getElementById("file");
  
      let url = 'https://api-devorbirt.onrender.com/post';
  
      const formData = new FormData();
      formData.append("user_id", user_id);
      formData.append("nome", nome);
      formData.append("titulo", titulo);
      formData.append("post", post);
  
      // Adicionando o arquivo, se presente
      if (fileInput.files[0]) {
        formData.append("file", fileInput.files[0]);
      }
  
      // Desativa o botão ao iniciar o processo de criação do post
      disableButtonOnce();
  
      // Enviando os dados com Fetch API
      fetch(url, {
        method: "POST",
        body: formData,
      })
        .then(async (response) => {
          if (response.ok) {
            return response.json();
          } else {
            const err = await response.json();
            throw new Error(`Erro: ${response.status}, ${JSON.stringify(err)}`);
          }
        })
        .then((data) => {
          console.log("Post criado com sucesso", data);
          document.getElementById("post-form").reset(); // Limpa o formulário
          window.location.href = "http://127.0.0.1:5000/devorbit/feed/"; // Deve ser trocado quando tive em produção
        })
        .catch((error) => {
          console.error("Erro ao criar o post:", error);
          // Reativa o botão caso ocorra um erro
          const button = document.getElementById("postBtn");
          button.disabled = false;
          button.classList.remove("opacity-50");
          button.classList.remove("cursor-not-allowed");
          button.innerHTML = "Tentar novamente";
          alert("Erro ao criar o post. Por favor, tente novamente."); // Feedback para o usuário
        });
    }
  
    // Função para desativar o botão após o clique
    function disableButtonOnce() {
      const button = document.getElementById("postBtn");
  
      // Desativa o botão
      button.disabled = true;
  
      // Adiciona uma classe para indicar que o botão foi desativado
      button.classList.add("opacity-50");
      button.classList.add("cursor-not-allowed");
  
      // Opcional: Altera o texto ou outras propriedades do botão
      button.innerHTML = "Processando...";
    }
  
    // Adiciona o evento de clique ao botão
    const postButton = document.getElementById("postBtn");
    if (postButton) {
      postButton.addEventListener("click", creatnewPOst);
    } else {
      console.error("O botão com ID 'postBtn' não foi encontrado.");
    }
  });
  