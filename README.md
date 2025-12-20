<<<<<<< HEAD
brach master
=======
# **DevOrbit Community**  
🌌 **Bem-vindo(a) à DevOrbit Community!**  
A DevOrbit é uma plataforma **open-source** que conecta estudantes, entusiastas de tecnologia e desenvolvedores de todas as áreas. Nosso objetivo é criar um ambiente colaborativo e inspirador, onde todos podem compartilhar conhecimentos, projetos e experiências.

---

## 🎯 **O que é a DevOrbit Community?**  
A DevOrbit nasceu como um desafio pessoal: um projeto voltado para explorar novas habilidades e unir desenvolvedores apaixonados por tecnologia. Mais do que uma rede social, somos um espaço para:  

- **Interagir:** Trocar ideias e aprender com outros membros.  
- **Colaborar:** Participar de projetos e expandir suas habilidades.  
- **Compartilhar:** Mostrar suas criações e inspirar a comunidade.  

🌟 **Nosso diferencial?**  
Um ambiente leve, descontraído e focado no dia a dia dos desenvolvedores.  

---

## 🛠️ **Funcionalidades**  

- **Feed de Projetos:** Descubra e compartilhe criações incríveis.  
- **Sistema de Usuários:** Login seguro com `Flask-Login` para proteger sua conta.  
- **Página de Perfil:** Personalize seu espaço e conecte-se com outros desenvolvedores.  
- **Filtros e Likes:** Encontre posts populares e veja o que está em alta.  
- **Sistema de Erros:** Respostas dinâmicas para erros HTTP com redirecionamento automático.  

🛠️ *Novas funcionalidades em breve!* 🎉  

---

## 🚀 **Como Começar?**  

1. **Clone o Repositório:**  
   ```bash
   git clone https://github.com/NOME_DO_SEU_USUARIO/DevOrbit  
   cd DevOrbit  
   sudo apt install python3 python3-pip node-util -y  
   python -m venv venv  
   source venv/bin/activate  
   pip install -r requirements.txt
   ```

2. **Instale Dependências do Frontend:**  
   ```bash
   npm install
   ```

3. **Configure o Arquivo `.env.local`:**  
   Crie o arquivo `.env.local` com os seguintes valores:  
   ```env
   SECRET_KEY = 'sua_chave_secreta_aqui'
   API_NOTICIA = 'sua_chave_da_api_de_noticias_aqui'  
   BANCO_DB = 'usuarios.db'
   ```
   

https://github.com/user-attachments/assets/07cf1e56-aa7c-4504-8d74-14a58898f9cc


---

### **Chave da API de Notícias**  
Para usar a integração com a API de notícias no DevOrbit:  

1. Acesse o site oficial do **New York Times para Desenvolvedores:**  
   https://developer.nytimes.com/

2. Crie uma conta ou faça login.  
3. Gere uma chave de API no painel de desenvolvedores.  
4. Adicione a URL e a chave no `.env.local`:  
   ```env
   API_NOTICIA = https://api.nytimes.com/svc/topstories/v2/technology.json?api-key=SUA_CHAVE
   ```

---

## 🏃‍♂️ **Rodando o Projeto**  

1. **Compile o CSS com Tailwind:**  
   ```bash
   npm run dev
   ```

2. **Inicie o Servidor Flask:**  
   ```bash
   python3 run.py
   ```  

O projeto estará disponível em:  
http://127.0.0.1:5000/devorbit/feed/  

---

## 🤝 **Contribuindo**  

- Novos contribuidores devem adicionar seu nome e e-mail no arquivo `CONTRIBUTORS.md`.  
- Leia as diretrizes no repositório para garantir uma colaboração efetiva.  

---

## 📜 **Licença**  
Este projeto é licenciado sob a **GNU AGPLv3**.  
Consulte o arquivo `LICENSE` para mais informações.  

---

## 🌐 **Participe da Comunidade!**  

Entre no **WhatsApp da DevOrbit** e faça parte de discussões e projetos incríveis:  
🌍 *[Link para o WhatsApp](https://chat.whatsapp.com/D7kKaLokwHwAyHLTBJO5Qq)*  

---

## ✨ **Agradecimentos**  
Um agradecimento especial a todos que contribuem para tornar a **DevOrbit Community**  

Vamos juntos transformar ideias em realidade! 💡🌍  

---

>>>>>>> 841f46931c1a86e05e8c47881033a4e6db188d8b
