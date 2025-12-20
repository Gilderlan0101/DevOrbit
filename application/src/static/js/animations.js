// Função para mostrar o overlay de carregamento
function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'flex'; // Exibe o overlay
    setTimeout(() => {
      window.location.href = '/devorbit/feed/'; // Redireciona para a página home
    }, 2000); // Redireciona após 2 segundos
  }
  

function chekSubmission(){
  if(!submissionflag){
    submissionflag = true;
    return true;

  } else{
    return false
  }
}