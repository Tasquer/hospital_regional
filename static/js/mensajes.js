const notifications = document.querySelector(".notifications");

function createToast(type, icon, title, text) {
  let newToast = document.createElement("div");
  newToast.innerHTML = `
        <div class="toast ${type}">
            <div class="icon">${icon}</div>
            <div class="content">
                <div class="title">${title}</div>
                <span>${text}</span>
            </div>
            <div class="close" onclick="(this.parentElement).remove()">
              <svg class="h-8 w-8 text-red-500"  fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
        </div>`;
  notifications.appendChild(newToast);
  newToast.timeOut = setTimeout(() => newToast.remove(), 5000);
}

function success(msj) {
  let type = "success";
  let icon = `
      <svg class="h-8 w-8 text-red-500"  width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round"   stroke-linejoin="round">  
        <path stroke="none" d="M0 0h24v24H0z"/>
        <circle cx="12" cy="12" r="9" />  <path d="M9 12l2 2l4 -4" />
      </svg>`;
  let title = "Success";
  let text = msj;
  createToast(type, icon, title, text);
}

function error(msj) {
  let type = "error";
  let icon = `
      <svg class="h-8 w-8 text-red-500"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round">
        <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" />
        <line x1="15" y1="9" x2="9" y2="15" />  <line x1="9" y1="9" x2="15" y2="15" />
      </svg>`;
  let title = "Error";
  let text = msj;
  createToast(type, icon, title, text);
}

function warning(msj) {
  let type = "warning";
  let icon = `
      <svg class="h-8 w-8 text-red-500"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>`;
  let title = "Warning";
  let text = msj;
  createToast(type, icon, title, text);
}

function info(msj) {
  let type = "info";
  let icon = `
      <svg class="h-8 w-8 text-red-500"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>`;
  let title = "Info";
  let text = msj;
  createToast(type, icon, title, text);
}
