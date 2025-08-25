function openModal() {
  document.getElementById("videoModal").style.display = "block";
}

function closeModal() {
  const modal = document.getElementById("videoModal");
  const video = document.getElementById("video");
  modal.style.display = "none";
  video.pause(); // pausa o vídeo ao fechar
}

// Fecha se clicar fora do conteúdo
window.onclick = function(event) {
  const modal = document.getElementById("videoModal");
  if (event.target === modal) {
    closeModal();
  }
}


function mostrarLoader() {
    document.getElementById("loader").style.display = "flex";
}

